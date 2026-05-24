from flask import Flask, render_template, session, jsonify, request, redirect, url_for
import os
import random
import sqlite3
import json
import hmac
import hashlib
from pathlib import Path
from urllib.parse import parse_qsl

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "dev-key-12345")

# Для Telegram WebApp на Render куки должны нормально жить внутри webview.
# Локально Secure отключен, иначе 127.0.0.1 не сможет поставить cookie.
IS_RENDER = bool(os.environ.get("RENDER"))
app.config.update(
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SECURE=IS_RENDER,
    SESSION_COOKIE_SAMESITE="None" if IS_RENDER else "Lax",
)


# ===== SQLite DB =====
# Для продакшена на Render лучше задать DATABASE_PATH=/var/data/app.db
# и подключить Persistent Disk. Без диска Render может сбрасывать SQLite при деплое.
def resolve_db_path() -> Path:
    explicit = os.environ.get("DATABASE_PATH")
    if explicit:
        return Path(explicit)

    data_dir = Path(os.environ.get("DATA_DIR", Path(app.root_path) / "data"))
    return data_dir / "app.db"


DB_PATH = resolve_db_path()


def get_db_connection():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    with get_db_connection() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS telegram_users (
                telegram_id INTEGER PRIMARY KEY,
                first_name TEXT,
                last_name TEXT,
                username TEXT,
                language_code TEXT,
                photo_url TEXT,
                allows_write_to_pm INTEGER DEFAULT 0,
                is_premium INTEGER DEFAULT 0,
                coins INTEGER NOT NULL DEFAULT 150,
                streak_days INTEGER NOT NULL DEFAULT 7,
                onboarding_seen INTEGER NOT NULL DEFAULT 0,
                card_of_day_json TEXT,
                last_init_data_hash TEXT,
                is_verified INTEGER NOT NULL DEFAULT 0,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                last_seen_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
            """
        )

        # Миграции для уже существующей app.db из GitHub/Render.
        columns = {row[1] for row in conn.execute("PRAGMA table_info(telegram_users)").fetchall()}
        migrations = {
            "allows_write_to_pm": "ALTER TABLE telegram_users ADD COLUMN allows_write_to_pm INTEGER DEFAULT 0",
            "is_premium": "ALTER TABLE telegram_users ADD COLUMN is_premium INTEGER DEFAULT 0",
            "coins": "ALTER TABLE telegram_users ADD COLUMN coins INTEGER NOT NULL DEFAULT 150",
            "streak_days": "ALTER TABLE telegram_users ADD COLUMN streak_days INTEGER NOT NULL DEFAULT 7",
            "onboarding_seen": "ALTER TABLE telegram_users ADD COLUMN onboarding_seen INTEGER NOT NULL DEFAULT 0",
            "card_of_day_json": "ALTER TABLE telegram_users ADD COLUMN card_of_day_json TEXT",
            "last_init_data_hash": "ALTER TABLE telegram_users ADD COLUMN last_init_data_hash TEXT",
            "is_verified": "ALTER TABLE telegram_users ADD COLUMN is_verified INTEGER NOT NULL DEFAULT 0",
            "created_at": "ALTER TABLE telegram_users ADD COLUMN created_at TEXT",
            "updated_at": "ALTER TABLE telegram_users ADD COLUMN updated_at TEXT",
            "last_seen_at": "ALTER TABLE telegram_users ADD COLUMN last_seen_at TEXT",
        }
        for column, sql in migrations.items():
            if column not in columns:
                conn.execute(sql)

        conn.execute("""
            UPDATE telegram_users
            SET
                created_at = COALESCE(created_at, CURRENT_TIMESTAMP),
                updated_at = COALESCE(updated_at, CURRENT_TIMESTAMP),
                last_seen_at = COALESCE(last_seen_at, CURRENT_TIMESTAMP)
        """)
        conn.commit()


def verify_telegram_init_data(init_data: str) -> bool:
    """Проверка подписи Telegram WebApp. Если BOT_TOKEN не задан, возвращаем False.
    Данные всё равно можно сохранить для локальной разработки, но is_verified будет 0.
    """
    bot_token = os.environ.get("BOT_TOKEN", "").strip()
    if not bot_token or not init_data:
        return False

    parsed = dict(parse_qsl(init_data, keep_blank_values=True))
    received_hash = parsed.pop("hash", None)
    if not received_hash:
        return False

    data_check_string = "\n".join(f"{key}={value}" for key, value in sorted(parsed.items()))
    secret_key = hmac.new(b"WebAppData", bot_token.encode("utf-8"), hashlib.sha256).digest()
    calculated_hash = hmac.new(secret_key, data_check_string.encode("utf-8"), hashlib.sha256).hexdigest()
    return hmac.compare_digest(calculated_hash, received_hash)


def normalize_tg_user(payload: dict) -> dict:
    """Принимает старый формат tgUser напрямую или новый {user, initData}."""
    if not isinstance(payload, dict):
        return {}
    user = payload.get("user") if isinstance(payload.get("user"), dict) else payload
    return user or {}


def get_user_by_telegram_id(telegram_id):
    if not telegram_id:
        return None
    with get_db_connection() as conn:
        return conn.execute(
            "SELECT * FROM telegram_users WHERE telegram_id = ?",
            (int(telegram_id),),
        ).fetchone()


def row_to_public_user(row):
    if not row:
        return {}
    return {
        "id": row["telegram_id"],
        "first_name": row["first_name"],
        "last_name": row["last_name"],
        "username": row["username"],
        "language_code": row["language_code"],
        "photo_url": row["photo_url"],
        "is_premium": bool(row["is_premium"]),
        "coins": row["coins"],
        "streak_days": row["streak_days"],
        "onboarding_seen": bool(row["onboarding_seen"]),
        "is_verified": bool(row["is_verified"]),
        "created_at": row["created_at"],
        "updated_at": row["updated_at"],
        "last_seen_at": row["last_seen_at"],
    }


def _clean_text(value):
    if value is None:
        return None
    value = str(value).strip()
    return value or None


def _bool_int(value):
    return 1 if value in (True, 1, "1", "true", "True", "yes", "on") else 0


def apply_client_state(row, state=None):
    """Мягко переносит состояние из localStorage в SQLite, когда Telegram-аккаунт наконец определился."""
    if not row or not isinstance(state, dict):
        return row

    updates = {}

    if state.get("onboarding_seen") is True or state.get("onboardingSeen") is True:
        updates["onboarding_seen"] = 1

    coins = state.get("coins")
    try:
        coins = int(coins)
        if 0 <= coins <= 1000000:
            updates["coins"] = coins
    except (TypeError, ValueError):
        pass

    streak_days = state.get("streak_days", state.get("streakDays"))
    try:
        streak_days = int(streak_days)
        if 0 <= streak_days <= 100000:
            updates["streak_days"] = streak_days
    except (TypeError, ValueError):
        pass

    card = state.get("card_of_day") or state.get("cardOfDay")
    if isinstance(card, dict):
        updates["card_of_day_json"] = json.dumps(card, ensure_ascii=False)

    if updates:
        session["tg_user_id"] = row["telegram_id"]
        update_user_state(**updates)
        return get_user_by_telegram_id(row["telegram_id"])

    return row


def upsert_telegram_user(tg_user: dict, init_data: str = "", client_state=None):
    telegram_id = tg_user.get("id")
    if not telegram_id:
        raise ValueError("telegram user id is required")

    is_verified = 1 if verify_telegram_init_data(init_data) else 0
    init_data_hash = hashlib.sha256(init_data.encode("utf-8")).hexdigest() if init_data else None

    first_name = _clean_text(tg_user.get("first_name"))
    last_name = _clean_text(tg_user.get("last_name"))
    username = _clean_text(tg_user.get("username"))
    language_code = _clean_text(tg_user.get("language_code"))
    photo_url = _clean_text(tg_user.get("photo_url"))

    with get_db_connection() as conn:
        conn.execute(
            """
            INSERT INTO telegram_users (
                telegram_id, first_name, last_name, username, language_code, photo_url,
                allows_write_to_pm, is_premium, last_init_data_hash, is_verified
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(telegram_id) DO UPDATE SET
                first_name = COALESCE(excluded.first_name, telegram_users.first_name),
                last_name = COALESCE(excluded.last_name, telegram_users.last_name),
                username = COALESCE(excluded.username, telegram_users.username),
                language_code = COALESCE(excluded.language_code, telegram_users.language_code),
                photo_url = COALESCE(excluded.photo_url, telegram_users.photo_url),
                allows_write_to_pm = CASE
                    WHEN excluded.allows_write_to_pm = 1 THEN 1
                    ELSE telegram_users.allows_write_to_pm
                END,
                is_premium = CASE
                    WHEN excluded.is_premium = 1 THEN 1
                    ELSE telegram_users.is_premium
                END,
                last_init_data_hash = COALESCE(excluded.last_init_data_hash, telegram_users.last_init_data_hash),
                is_verified = CASE WHEN excluded.is_verified = 1 THEN 1 ELSE telegram_users.is_verified END,
                updated_at = CURRENT_TIMESTAMP,
                last_seen_at = CURRENT_TIMESTAMP
            """,
            (
                int(telegram_id),
                first_name,
                last_name,
                username,
                language_code,
                photo_url,
                _bool_int(tg_user.get("allows_write_to_pm")),
                _bool_int(tg_user.get("is_premium")),
                init_data_hash,
                is_verified,
            ),
        )
        conn.commit()

    row = get_user_by_telegram_id(telegram_id)
    row = apply_client_state(row, client_state)
    return row


def sync_session_from_db(row):
    if not row:
        return
    session["tg_user_id"] = row["telegram_id"]
    session["tg_user"] = row_to_public_user(row)
    session["coins"] = row["coins"]
    session["streak_days"] = row["streak_days"]
    session["onboarding_seen"] = bool(row["onboarding_seen"])
    if row["card_of_day_json"]:
        try:
            session["card_of_day"] = json.loads(row["card_of_day_json"])
        except json.JSONDecodeError:
            session.pop("card_of_day", None)


def update_user_state(**fields):
    telegram_id = session.get("tg_user_id")
    if not telegram_id or not fields:
        return

    allowed = {"coins", "streak_days", "onboarding_seen", "card_of_day_json"}
    updates = {key: value for key, value in fields.items() if key in allowed}
    if not updates:
        return

    set_clause = ", ".join(f"{key} = ?" for key in updates)
    values = list(updates.values()) + [int(telegram_id)]
    with get_db_connection() as conn:
        conn.execute(
            f"UPDATE telegram_users SET {set_clause}, updated_at = CURRENT_TIMESTAMP WHERE telegram_id = ?",
            values,
        )
        conn.commit()

init_db()


# ===== МИНИМАЛЬНЫЕ ДАННЫЕ =====

SIMPLE_CARDS = [
    {
        "id": 1,
        "name": "Шут",
        "meaning": "новое начало, свобода и доверие пути"
    },
    {
        "id": 2,
        "name": "Маг",
        "meaning": "сила намерения и способность проявить желаемое"
    },
    {
        "id": 3,
        "name": "Жрица",
        "meaning": "интуиция, внутреннее знание и тишина"
    },
    {
        "id": 4,
        "name": "Сила",
        "meaning": "мягкая уверенность, терпение и внутренняя опора"
    },
    {
        "id": 5,
        "name": "Звезда",
        "meaning": "надежда, вдохновение и восстановление"
    },
]


def init_session():
    # Если пользователь уже сохранен в SQLite, подтягиваем его состояние по Telegram ID.
    if session.get("tg_user_id"):
        row = get_user_by_telegram_id(session.get("tg_user_id"))
        if row:
            sync_session_from_db(row)

    if "coins" not in session:
        session["coins"] = 150

    if "streak_days" not in session:
        session["streak_days"] = 7

    if "onboarding_seen" not in session:
        session["onboarding_seen"] = False

    session.modified = True


@app.context_processor
def inject_tg_user():
    return {
        "tg_user": session.get("tg_user", {}),
        "db_path": str(DB_PATH),
    }
# ===== ONBOARDING =====

@app.route("/onboarding")
def onboarding():
    return redirect(url_for("onboarding_1"))


@app.route("/onboarding/1")
def onboarding_1():
    return render_template("onboarding1.html")


@app.route("/onboarding/2")
def onboarding_2():
    return render_template("onboarding2.html")

@app.route('/loading')
def loading():
    return render_template('loading.html')

@app.route("/vip")
def vip():
    return redirect(url_for("career_full"))


@app.route("/vip-old")
def vip_old():
    return render_template("vip.html")

@app.route("/onboarding/3")
def onboarding_3():
    return render_template("onboarding3.html")


@app.route("/onboarding/finish")
def onboarding_finish():
    session["onboarding_seen"] = True
    session.modified = True
    update_user_state(onboarding_seen=1)
    return redirect(url_for("today"))


@app.route("/reset-onboarding")
def reset_onboarding():
    session["onboarding_seen"] = False
    update_user_state(onboarding_seen=0)
    return redirect(url_for("onboarding_1"))


# ===== MAIN PAGES =====

@app.route("/")
@app.route("/today")
def today():
    init_session()

    if not session.get("onboarding_seen"):
        return redirect(url_for("onboarding_1"))

    return render_template(
        "today.html",
        coins=session.get("coins", 150),
        streak_days=session.get("streak_days", 7),
        card_of_day=session.get("card_of_day"),
        tg_user=session.get("tg_user", {})
    )


@app.route("/profile")
def profile():
    init_session()
    return render_template(
        "profile.html",
        coins=session.get("coins", 150),
        tg_user=session.get("tg_user", {})
    )


@app.route("/settings")
def settings():
    return render_template("settings.html")


@app.route("/collection")
def collection():
    init_session()
    return render_template(
        "collection.html",
        coins=session.get("coins", 150),
        collected=[],
        progress=0,
        total=78
    )


@app.route("/match")
def match():
    return render_template("match.html")
@app.route('/birthdateGotovo')
def birthdate1():
    return render_template('birthdate.html')
@app.route("/birthplace")
def birthplace():
    return render_template("birthplace.html")
@app.route("/birthtime")
def birthtime():
    return render_template("birthtime_1to1.html")
@app.route("/birthdate")
def birthdate():
    return render_template("birthdate_1to1.html")

@app.route("/match2")
def match2():
    return render_template("match2.html")
@app.route('/loading1')
def loading1():
    return render_template('loading_1to1.html')


@app.route("/quiz0")
def quiz0():
    return redirect(url_for("today"))

@app.route("/quiz1")
def quiz1():
    return render_template("quiz1.html")


@app.route("/quiz2")
def quiz2():
    return render_template("quiz2.html")

@app.route("/result1")
def result1():
    return render_template("result_1to1.html")


@app.route("/career-full")
@app.route("/career-money-full")
@app.route("/vip-result")
def career_full():
    return render_template("career_full.html")


@app.route("/love-result")
@app.route("/love-relationships")
@app.route("/relationship-result")
def love_result():
    return render_template("love_result.html")


@app.route("/love-full")
@app.route("/love-relationships-full")
@app.route("/relationship-full")
@app.route("/love-vip-result")
def love_full():
    return render_template("love_full.html")

@app.route("/quiz3")
def quiz3():
    return render_template("quiz3.html")


@app.route("/quiz4")
def quiz4():
    return render_template("quiz4.html")


@app.route("/quiz5")
def quiz5():
    return render_template("quiz5.html")


@app.route("/result")
def result():
    return render_template("result.html")


@app.route("/compatibility-upsell")
@app.route("/result-upsell")
@app.route("/compatibility-vip")
def compatibility_upsell():
    return render_template("compatibility_upsell.html")


@app.route("/quick-spreads")
def quick_spreads():
    return render_template("quick.html")


# ===== API =====

@app.route("/api/draw-card", methods=["POST"])
def draw_card():
    init_session()

    card = random.choice(SIMPLE_CARDS)
    session["card_of_day"] = card
    session["coins"] = session.get("coins", 150) + 5
    update_user_state(
        coins=session["coins"],
        card_of_day_json=json.dumps(card, ensure_ascii=False)
    )

    return jsonify({
        "success": True,
        "card": card,
        "coins": session["coins"]
    })


@app.route("/api/compatibility", methods=["POST"])
def compatibility():
    data = request.get_json(silent=True) or {}
    name = data.get("name", "")

    return jsonify({
        "success": True,
        "name": name,
        "compatibility": random.randint(60, 100)
    })

@app.route("/save-user", methods=["POST"])
def save_user():
    data = request.get_json(silent=True) or {}
    tg_user = normalize_tg_user(data)
    init_data = data.get("initData", "") if isinstance(data, dict) else ""
    client_state = data.get("state", {}) if isinstance(data, dict) else {}

    try:
        row = upsert_telegram_user(tg_user, init_data=init_data, client_state=client_state)
    except ValueError as exc:
        return jsonify({"success": False, "error": str(exc)}), 400

    sync_session_from_db(row)

    return jsonify({
        "success": True,
        "user": row_to_public_user(row),
        "state": get_public_state(row),
        "db": str(DB_PATH),
    })


def get_public_state(row=None):
    if row is None and session.get("tg_user_id"):
        row = get_user_by_telegram_id(session.get("tg_user_id"))
    if row:
        card = None
        if row["card_of_day_json"]:
            try:
                card = json.loads(row["card_of_day_json"])
            except json.JSONDecodeError:
                card = None
        return {
            "coins": row["coins"],
            "streak_days": row["streak_days"],
            "onboarding_seen": bool(row["onboarding_seen"]),
            "card_of_day": card,
        }
    return {
        "coins": session.get("coins", 150),
        "streak_days": session.get("streak_days", 7),
        "onboarding_seen": bool(session.get("onboarding_seen")),
        "card_of_day": session.get("card_of_day"),
    }


@app.route("/api/state", methods=["GET", "POST"])
def api_state():
    init_session()

    if request.method == "POST":
        data = request.get_json(silent=True) or {}

        # Если клиент одновременно прислал Telegram user, сначала авторизуем/создадим запись.
        if isinstance(data.get("user"), dict) or data.get("id"):
            tg_user = normalize_tg_user(data)
            init_data = data.get("initData", "")
            try:
                row = upsert_telegram_user(tg_user, init_data=init_data, client_state=data.get("state", data))
                sync_session_from_db(row)
            except ValueError:
                pass

        updates = {}

        if "coins" in data:
            try:
                coins = int(data.get("coins"))
                if 0 <= coins <= 1000000:
                    session["coins"] = coins
                    updates["coins"] = coins
            except (TypeError, ValueError):
                pass

        if "streak_days" in data or "streakDays" in data:
            try:
                streak_days = int(data.get("streak_days", data.get("streakDays")))
                if 0 <= streak_days <= 100000:
                    session["streak_days"] = streak_days
                    updates["streak_days"] = streak_days
            except (TypeError, ValueError):
                pass

        if data.get("onboarding_seen") is True or data.get("onboardingSeen") is True:
            session["onboarding_seen"] = True
            updates["onboarding_seen"] = 1
        elif data.get("onboarding_seen") is False:
            session["onboarding_seen"] = False
            updates["onboarding_seen"] = 0

        if isinstance(data.get("card_of_day"), dict):
            session["card_of_day"] = data["card_of_day"]
            updates["card_of_day_json"] = json.dumps(data["card_of_day"], ensure_ascii=False)

        if updates:
            update_user_state(**updates)
            session.modified = True

    row = get_user_by_telegram_id(session.get("tg_user_id"))
    if row:
        sync_session_from_db(row)

    return jsonify({
        "success": True,
        "user": row_to_public_user(row) if row else session.get("tg_user", {}),
        "state": get_public_state(row),
    })


@app.route("/api/me")
def api_me():
    init_session()
    row = get_user_by_telegram_id(session.get("tg_user_id"))
    return jsonify({
        "success": bool(row),
        "user": row_to_public_user(row) if row else session.get("tg_user", {}),
        "state": get_public_state(row),
    })


@app.route("/health")
def health():
    return {"status": "ok"}



if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)

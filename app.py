from flask import Flask, render_template, session, jsonify, request, redirect, url_for
import os
import random

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "dev-key-12345")


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
    if "coins" not in session:
        session["coins"] = 150

    if "streak_days" not in session:
        session["streak_days"] = 7

@app.context_processor
def inject_tg_user():
    return {
        "tg_user": session.get("tg_user", {})
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
    return render_template("vip.html")

@app.route("/onboarding/3")
def onboarding_3():
    return render_template("onboarding3.html")


@app.route("/onboarding/finish")
def onboarding_finish():
    session["onboarding_seen"] = True
    return redirect(url_for("today"))


@app.route("/reset-onboarding")
def reset_onboarding():
    session.pop("onboarding_seen", None)
    return redirect(url_for("today"))


# ===== MAIN PAGES =====

@app.route("/")
def today():
    if not session.get("onboarding_seen"):
        return redirect(url_for("onboarding_1"))

    init_session()

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
        coins=session.get("coins", 150)
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

@app.route("/quiz1")
def quiz1():
    return render_template("quiz1.html")


@app.route("/quiz2")
def quiz2():
    return render_template("quiz2.html")

@app.route("/result1")
def result1():
    return render_template("result_1to1.html")

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


# ===== API =====

@app.route("/api/draw-card", methods=["POST"])
def draw_card():
    init_session()

    card = random.choice(SIMPLE_CARDS)
    session["card_of_day"] = card
    session["coins"] = session.get("coins", 150) + 5

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

    session["tg_user"] = {
        "id": data.get("id"),
        "first_name": data.get("first_name"),
        "last_name": data.get("last_name"),
        "username": data.get("username"),
        "photo_url": data.get("photo_url")
    }

    return jsonify({"success": True})


@app.route("/health")
def health():
    return {"status": "ok"}


port = int(os.environ.get("PORT", 5000))
app.run(host="0.0.0.0", port=port)

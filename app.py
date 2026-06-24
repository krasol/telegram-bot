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




SPREAD_READY_SCREENS = {'love': {'slug': 'love',
          'title': 'Расклад на любовь',
          'heading': 'Расклад на\nлюбовь',
          'description': 'Карты помогут понять скрытые чувства,\n'
                         'эмоциональную связь и возможное будущее\n'
                         'ваших отношений.',
          'options': ['Чувства', 'Истинные намерения', 'Будущее'],
          'back_url': '/spreads',
          'start_url': '/spread/love/focus',
          'focus_title': 'Сконцентрируйся\nна человеке',
          'focus_description': 'Подумайте о ваших отношениях, пока карты считывают энергию вашей связи.',
          'shuffle_url': '/loading'},
 'breakup': {'slug': 'breakup',
             'title': 'Расклад после расставания',
             'heading': 'Расклад после\nрасставания',
             'description': 'Карты покажут, почему отношения\n'
                            'завершились, какие чувства остались\n'
                            'и что ждёт вас дальше.',
             'options': ['Причины', 'Чувства', 'Будущее'],
             'back_url': '/spreads',
             'start_url': '/spread/breakup/focus',
             'focus_title': 'Отпусти лишние\nэмоции',
             'focus_description': 'Сделай глубокий вдох и отпусти обиду. Карты покажут истинные причины и что важно понять после разрыва.',
             'shuffle_url': '/loading'},
 'career': {'slug': 'career',
            'title': 'Расклад на карьеру',
            'heading': 'Расклад\nна карьеру',
            'description': 'Карты помогут увидеть направление\n'
                           'карьерного пути, точки роста\n'
                           'и ваш профессиональный результат.',
            'options': ['Текущий карьерный фокус', 'Точка максимального роста', 'Ваш профессиональный результат'],
            'back_url': '/spreads',
            'start_url': '/spread/career/focus',
            'focus_title': 'Настройтесь\nна свой успех',
            'focus_description': 'Вспомните вашу текущую ситуацию, цели и сомнения. Карты помогут увидеть, что мешает развитию и куда стоит двигаться дальше.',
            'shuffle_url': '/loading'},
 'finance': {'slug': 'finance',
             'title': 'Финансовый путь',
             'heading': 'Финансовый путь',
             'description': 'Этот расклад поможет понять, откуда\n'
                            'может прийти финансовый поток, где\n'
                            'скрыты возможности и сложности.',
             'options': ['Источники дохода', 'Текущие финансовые сложности', 'Ваш профессиональный результат'],
             'back_url': '/spreads',
             'start_url': '/spread/finance/focus',
             'focus_title': 'Настройтесь\nна энергию\nизобилия',
             'focus_description': 'Закройте глаза на несколько секунд и подумайте о своём финпотоке. Представьте желаемый уровень дохода, свои цели и то, чего вы хотите достичь.',
             'shuffle_url': '/loading'},
 'future': {'slug': 'future',
            'title': 'Что ждёт впереди',
            'heading': 'Что ждёт впереди',
            'description': 'Карты покажут скрытые шансы,\nближайший поворот судьбы\nи вероятный исход событий.',
            'options': ['Скрытые возможности', 'Ближайший поворот судьбы', 'Вероятный исход событий'],
            'back_url': '/spreads',
            'start_url': '/spread/future/focus',
            'focus_title': 'Откройтесь\nбудущему',
            'focus_description': 'Не пытайтесь контролировать ответ или представить желаемый результат. Просто доверьтесь потоку событий и позвольте картам показать то, что готовит для вас судьба.',
            'shuffle_url': '/loading'},
 'purpose': {'slug': 'purpose',
             'title': 'Ваше предназначение',
             'heading': 'Ваше\nпредназначение',
             'description': 'Этот расклад поможет понять, какие таланты\n'
                            'заложены в вас от природы, что мешает\n'
                            'раскрыться и куда ведёт ваша душа.',
             'options': ['Дар, которым стоит служить', 'Что блокирует мою реализацию', 'Путь моей души'],
             'back_url': '/spreads',
             'start_url': '/spread/purpose/focus',
             'focus_title': 'Услышьте свой\nвнутренний голос',
             'focus_description': 'Подумайте о том, чем вам действительно нравится заниматься, что вдохновляет вас и приносит ощущение смысла.',
             'shuffle_url': '/loading'}}


SPREAD_SELECT_DATA = {
    "love": {
        "select_options": ["Мысли", "Чувства", "Будущее"],
        "select_hint": "Каждая карта раскроет скрытый\nаспект вашей ситуации",
        "result_url": "/loading",
    },
    "breakup": {
        "select_options": ["Причины разрыва", "Его чувства сейчас", "Возможность возвращения"],
        "select_hint": "Каждая карта даст ответ\nо прошлом и чувствах",
        "result_url": "/loading",
    },
    "career": {
        "select_options": ["Главный карьерный барьер", "Точка максимального роста", "Ваш результат"],
        "select_hint": "Каждая карта откроет\nважную часть карьерного пути",
        "result_url": "/loading",
    },
    "finance": {
        "select_options": ["Что перекрывает поток", "Где скрыта возможность", "Истинный путь"],
        "select_hint": "Каждая карта покажет\nчасть вашего финансового пути",
        "result_url": "/loading",
    },
    "future": {
        "select_options": ["Скрытые силы ситуации", "Ближайший поворот судьбы", "Вероятный исход событий"],
        "select_hint": "Каждая карта откроет шанс, путь\nи вероятный финал событий",
        "result_url": "/loading",
    },
    "purpose": {
        "select_options": ["Дар, данный вам от рождения", "Что блокирует вашу реализацию", "Путь вашей души"],
        "select_hint": "Каждая карта поможет услышать\nчасть вашего истинного предназначения",
        "result_url": "/loading",
    },
}

for _slug, _select_data in SPREAD_SELECT_DATA.items():
    if _slug in SPREAD_READY_SCREENS:
        SPREAD_READY_SCREENS[_slug].update(_select_data)
        SPREAD_READY_SCREENS[_slug]["select_url"] = f"/spread/{_slug}/select"
        SPREAD_READY_SCREENS[_slug]["loading_url"] = f"/spread/{_slug}/loading"
        SPREAD_READY_SCREENS[_slug]["final_result_url"] = f"/spread/{_slug}/result"
        SPREAD_READY_SCREENS[_slug]["result_url"] = SPREAD_READY_SCREENS[_slug]["loading_url"]
        SPREAD_READY_SCREENS[_slug]["finish_url"] = "/spreads"
        SPREAD_READY_SCREENS[_slug]["result_image"] = f"img/spread-results/{_slug}.png"
        SPREAD_READY_SCREENS[_slug]["shuffle_url"] = SPREAD_READY_SCREENS[_slug]["select_url"]




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


@app.route("/spreads")
def spreads():
    init_session()
    return render_template("spreads.html")


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

SPREAD_RESULTS = {
    "love": {
        "items": [
            {"icon": "brain.svg", "color": "#F0C533", "title": "Мысли: Рациональное начало", "text": "Ваш партнёр сейчас погружён в раздумья о стабильности ваших отношений. В его голове выстраивается чёткий план будущего, где доверие является фундаментом."},
            {"icon": "heart.svg", "color": "#F3B8FF", "title": "Чувства: Глубина души", "text": "На эмоциональном уровне царит гармония, изображённая картой «Влюблённые». Это время сильного притяжения и искреннего желания разделить свой путь с вами."},
            {"icon": "sparkle.svg", "color": "#F0C533", "title": "Будущее: Звездный путь", "text": "Карта «Звезда» обещает исцеление прошлых обид и новый светлый этап. Ваши совместные мечты начнут обретать форму в реальности в ближайшие три лунных цикла."},
        ]
    },
    "breakup": {
        "items": [
            {"icon": "brain.svg", "color": "#F0C533", "title": "Причина разрыва", "text": "Ваш партнёр сейчас погружён в раздумья о стабильности ваших отношений. В его голове выстраивается чёткий план будущего, где доверие является фундаментом."},
            {"icon": "heart.svg", "color": "#F3B8FF", "title": "Его чувства сейчас", "text": "На эмоциональном уровне царит гармония, изображённая картой «Влюблённые». Это время сильного притяжения и искреннего желания разделить свой путь с вами."},
            {"icon": "key.svg", "color": "#F0C533", "title": "Возможность возвращения", "text": "Карта «Звезда» обещает исцеление прошлых обид и новый светлый этап. Ваши совместные мечты начнут обретать форму в реальности в ближайшие три лунных цикла."},
        ]
    },
    "career": {
        "items": [
            {"icon": "warning.svg", "color": "#F0C533", "title": "Главный карьерный барьер", "text": "Вы достигли точки, где привычные методы больше не дают прежнего результата. Карта показывает, что главным препятствием становится нежелание выйти из зоны комфорта."},
            {"icon": "target.svg", "color": "#E2B2FF", "title": "Точка максимального роста", "text": "Сейчас наиболее перспективным направлением является развитие навыков и расширение профессиональных связей. Возможность, которую вы ищете, придёт через людей вокруг вас."},
            {"icon": "trophy.svg", "color": "#F0C533", "title": "Профессиональный результат", "text": "Если вы продолжите двигаться вперёд и не свернёте с выбранного пути, впереди вас ждёт признание ваших заслуг и заметный карьерный рост."},
        ]
    },
    "finance": {
        "items": [
            {"icon": "warning.svg", "color": "#F0C533", "title": "Что тормозит развитие", "text": "Вы достигли точки, где привычные методы больше не дают прежнего результата. Карта показывает, что главным препятствием становится нежелание выйти из зоны комфорта."},
            {"icon": "target.svg", "color": "#E2B2FF", "title": "Куда направить усилия", "text": "Сейчас наиболее перспективным направлением является развитие навыков и расширение профессиональных связей. Возможность, которую вы ищете, придёт через людей вокруг вас."},
            {"icon": "trophy.svg", "color": "#F0C533", "title": "Итог ваших действий", "text": "Если вы продолжите двигаться вперёд и не свернёте с выбранного пути, впереди вас ждёт признание ваших заслуг и заметный карьерный рост."},
        ]
    },
    "future": {
        "items": [
            {"icon": "moon.svg", "color": "#F0C533", "title": "Скрытые силы ситуации", "text": "Эта карта показывает процессы и обстоятельства, которые уже влияют на вашу жизнь, но пока остаются незаметными. Именно здесь скрываются причины многих будущих событий."},
            {"icon": "sparkle.svg", "color": "#E2B2FF", "title": "Ближайший поворот судьбы", "text": "Здесь раскрывается событие или встреча, способная изменить ход текущей ситуации. Карта указывает на возможность, решение или знак, который появится в ближайшее время."},
            {"icon": "crystal.svg", "color": "#F0C533", "title": "Вероятный исход событий", "text": "Эта карта показывает наиболее вероятное развитие ситуации при сохранении текущего курса. Она помогает увидеть перспективу и подготовиться к будущим переменам."},
        ]
    },
    "purpose": {
        "items": [
            {"icon": "compass.svg", "color": "#F0C533", "title": "Дар, данный вам от рождения", "text": "Эта карта раскрывает качества и способности, которые являются вашей природной силой. Именно через них вы способны достигать наибольших результатов и чувствовать внутреннюю гармонию."},
            {"icon": "flame.svg", "color": "#F3B8FF", "title": "Что блокирует реализацию", "text": "Здесь карты показывают препятствие, которое не позволяет вам полностью раскрыть свой потенциал. Это может быть страх, внутренняя неуверенность или ситуация, требующая переосмысления."},
            {"icon": "star.svg", "color": "#F0C533", "title": "Путь вашей души", "text": "Эта карта показывает направление, в котором вы сможете наиболее полно реализовать себя. Она помогает понять, куда стоит направить свою энергию, чтобы почувствовать удовлетворение, уверенность и смысл."},
        ]
    },
}

def get_tarot_card_files():
    card_dir = os.path.join(app.static_folder, "img", "tarot-cards")
    if not os.path.isdir(card_dir):
        return []
    files = []
    for name in sorted(os.listdir(card_dir)):
        if name.lower().endswith((".png", ".jpg", ".jpeg", ".webp")):
            files.append(f"img/tarot-cards/{name}")
    return files



def prepare_spread_screen(slug):
    screen = SPREAD_READY_SCREENS.get(slug)
    if not screen:
        return None
    screen = dict(screen)
    screen["back_url"] = "/spreads"
    screen["start_url"] = f"/spread/{slug}/focus"
    screen["shuffle_url"] = f"/spread/{slug}/select"
    screen["result_url"] = f"/spread/{slug}/loading"
    screen["final_result_url"] = f"/spread/{slug}/result"
    return screen


@app.route("/spread/<slug>")
def spread_ready(slug):
    screen = prepare_spread_screen(slug)
    if not screen:
        return redirect(url_for("spreads"))
    return render_template("spread_ready.html", screen=screen)


@app.route("/spread/<slug>/focus")
def spread_focus(slug):
    screen = prepare_spread_screen(slug)
    if not screen:
        return redirect(url_for("spreads"))
    return render_template("spread_focus.html", screen=screen)


@app.route("/spread/<slug>/select")
def spread_select(slug):
    screen = prepare_spread_screen(slug)
    if not screen:
        return redirect(url_for("spreads"))
    return render_template("spread_select.html", screen=screen)


@app.route("/spread/<slug>/loading")
def spread_loading(slug):
    screen = prepare_spread_screen(slug)
    if not screen:
        return redirect(url_for("spreads"))
    return render_template("spread_loading.html", screen=screen)


@app.route("/spread/<slug>/result")
def spread_result(slug):
    spread = SPREAD_RESULTS.get(slug)
    if not spread:
        return redirect(url_for("spreads"))

    cards = get_tarot_card_files()
    if len(cards) >= 3:
        random_cards = random.sample(cards, 3)
    else:
        random_cards = ["img/tarot-card.png", "img/tarot-card.png", "img/tarot-card.png"]

    return render_template("spread_result.html", spread=spread, cards=random_cards, spread_key=slug)


@app.route("/compatibility")
def compatibility_page():
    return render_template("compatibility.html")
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

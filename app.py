import logging
from flask import Flask, render_template, jsonify, request, session
from datetime import datetime, timedelta
import random
import json
import os

# Настройка логирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# ============= СОЗДАЕМ FLASK ПРИЛОЖЕНИЕ =============
app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'dev-key-12345')

# ============= ДАННЫЕ =============

# Карты Таро (78 карт)
TAROT_CARDS = [
    {"id": 0, "name": "Шут", "meaning": "Новое начало, спонтанность"},
    {"id": 1, "name": "Маг", "meaning": "Сила воли, мастерство"},
    {"id": 2, "name": "Верховная Жрица", "meaning": "Интуиция, тайна"},
    {"id": 3, "name": "Императрица", "meaning": "Изобилие, плодородие"},
    {"id": 4, "name": "Император", "meaning": "Власть, структура"},
    {"id": 5, "name": "Иерофант", "meaning": "Традиции, мудрость"},
    {"id": 6, "name": "Влюбленные", "meaning": "Выбор, отношения"},
    {"id": 7, "name": "Колесница", "meaning": "Воля, победа"},
    {"id": 8, "name": "Сила", "meaning": "Мужество, внутренняя сила"},
    {"id": 9, "name": "Отшельник", "meaning": "Поиск, уединение"},
    {"id": 10, "name": "Колесо Фортуны", "meaning": "Перемены, судьба"},
    {"id": 11, "name": "Справедливость", "meaning": "Честность, баланс"},
    {"id": 12, "name": "Повешенный", "meaning": "Жертва, новый взгляд"},
    {"id": 13, "name": "Смерть", "meaning": "Трансформация, конец"},
    {"id": 14, "name": "Умеренность", "meaning": "Баланс, гармония"},
    {"id": 15, "name": "Дьявол", "meaning": "Зависимость, материализм"},
    {"id": 16, "name": "Башня", "meaning": "Разрушение, прорыв"},
    {"id": 17, "name": "Звезда", "meaning": "Надежда, вдохновение"},
    {"id": 18, "name": "Луна", "meaning": "Иллюзии, подсознание"},
    {"id": 19, "name": "Солнце", "meaning": "Радость, успех"},
    {"id": 20, "name": "Суд", "meaning": "Возрождение, призвание"},
    {"id": 21, "name": "Мир", "meaning": "Завершение, целостность"}
]  # Здесь добавим остальные карты

# Энергии дня
ENERGIES = ["🔥 Высокая", "💧 Спокойная", "🌪 Нестабильная", "⛰ Устойчивая", "✨ Творческая"]

# Гороскопы для знаков зодиака
HOROSCOPES = {
    "aries": "♈ Овен: Сегодня звезды благосклонны к новым начинаниям",
    "taurus": "♉ Телец: День подходит для финансовых решений",
    "gemini": "♊ Близнецы: Общение принесет удачу",
    "cancer": "♋ Рак: Слушайте интуицию",
    "leo": "♌ Лев: Сегодня ваш день",
    "virgo": "♍ Дева: Внимание к деталям",
    "libra": "♎ Весы: Найдите баланс",
    "scorpio": "♏ Скорпион: Трансформация",
    "sagittarius": "♐ Стрелец: Приключения ждут",
    "capricorn": "♑ Козерог: Упорство окупится",
    "aquarius": "♒ Водолей: Новые идеи",
    "pisces": "♓ Рыбы: Доверьтесь потоку"
}


# ============= ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ =============

def init_user_session():
    """Инициализация сессии пользователя"""
    if 'coins' not in session:
        session['coins'] = 100  # Стартовые монеты
    if 'collected_cards' not in session:
        session['collected_cards'] = []
    if 'has_subscription' not in session:
        session['has_subscription'] = False


# ============= МАРШРУТЫ =============

@app.route('/')
def index():
    """Входная точка"""
    init_user_session()
    return render_template('index.html')


@app.route('/today')
def today():
    """Главный экран 'Сегодня'"""
    init_user_session()

    # Проверяем, заходил ли сегодня пользователь
    last_visit = session.get('last_visit')
    today_str = datetime.now().strftime('%Y-%m-%d')

    if last_visit != today_str:
        # Новый день - даем монеты за вход
        session['coins'] = session.get('coins', 0) + 10
        session['last_visit'] = today_str
        session['daily_bonus'] = True
    else:
        session['daily_bonus'] = False

    # Получаем данные для отображения
    context = {
        'active': 'today',
        'card_of_day': session.get('card_of_day'),
        'energy': random.choice(ENERGIES),
        'horoscope': HOROSCOPES.get(session.get('zodiac', 'aries')),
        'coins': session.get('coins', 0),
        'daily_bonus': session.get('daily_bonus', False)
    }

    return render_template('today.html', **context)


@app.route('/tarot')
def tarot():
    """Раздел Таро"""
    init_user_session()
    return render_template('tarot.html', active='tarot')


@app.route('/card-of-day')
def card_of_day():
    """Карта дня"""
    init_user_session()

    card = session.get('card_of_day')
    collected = len(session.get('collected_cards', []))

    return render_template('card_of_day.html',
                           active='tarot',
                           card=card,
                           collected=collected,
                           progress=int((collected / 78) * 100))


@app.route('/collection')
def collection():
    """Коллекция карт"""
    init_user_session()

    collected = session.get('collected_cards', [])
    progress = len(collected)
    total = 78

    return render_template('collection.html',
                           active='collection',
                           collected=collected,
                           progress=progress,
                           total=total)


@app.route('/quick-spreads')
def quick_spreads():
    """Быстрые расклады"""
    init_user_session()

    # Проверяем бесплатный расклад на неделе
    week_key = f'free_spread_week_{datetime.now().strftime("%Y-%W")}'
    free_spreads = 0 if session.get(week_key) else 1

    return render_template('quick.html',
                           active='tarot',
                           free_spreads=free_spreads)


@app.route('/deep-spreads')
def deep_spreads():
    """Глубокие расклады"""
    init_user_session()
    return render_template('deep.html', active='tarot')


@app.route('/profile')
def profile():
    """Профиль пользователя"""
    init_user_session()
    return render_template('profile.html', active='profile')


# ============= API =============

@app.route('/api/draw-card', methods=['POST'])
def draw_card():
    """Тянет случайную карту"""
    init_user_session()

    card = random.choice(TAROT_CARDS)

    # Сохраняем как карту дня
    session['card_of_day'] = card

    # Добавляем в коллекцию
    collected = session.get('collected_cards', [])
    if card['id'] not in collected:
        collected.append(card['id'])
        session['collected_cards'] = collected

        # Даем монеты за новую карту
        session['coins'] = session.get('coins', 0) + 5

    return jsonify({
        'success': True,
        'card': card,
        'coins': session.get('coins', 0)
    })


@app.route('/api/get-deep-reading', methods=['POST'])
def get_deep_reading():
    """Глубокая интерпретация (платная)"""
    init_user_session()

    data = request.json
    card_id = data.get('card_id')

    # Проверяем монеты
    if session.get('coins', 0) < 50:
        return jsonify({'success': False, 'error': 'Недостаточно монет'})

    # Списываем монеты
    session['coins'] = session.get('coins', 0) - 50

    # Находим карту
    card = next((c for c in TAROT_CARDS if c['id'] == card_id), None)

    if not card:
        return jsonify({'success': False, 'error': 'Карта не найдена'})

    # Генерируем глубокую интерпретацию
    deep_meanings = {
        "Новое начало": "В вашей жизни наступает период новых возможностей...",
        "Сила воли": "Ваша внутренняя сила сейчас на пике...",
        "Интуиция": "Доверьтесь своему внутреннему голосу..."
    }

    deep_meaning = deep_meanings.get(card['meaning'].split(',')[0],
                                     f"Подробное значение карты {card['name']}: {card['meaning']}. В ближайшее время эта энергия будет влиять на ваши решения...")

    return jsonify({
        'success': True,
        'meaning': deep_meaning,
        'coins': session['coins']
    })


@app.route('/api/quick-spread', methods=['POST'])
def quick_spread():
    """Быстрый расклад по теме"""
    init_user_session()

    data = request.json
    topic = data.get('topic')

    # Цены на расклады
    prices = {
        'love': 10,
        'money': 10,
        'future': 10,
        'thoughts': 15,
        'yesno': 5
    }

    price = prices.get(topic, 10)

    # Проверяем бесплатный расклад на неделе
    week_key = f'free_spread_week_{datetime.now().strftime("%Y-%W")}'
    free_used = session.get(week_key, False)

    if not free_used:
        # Первый бесплатный расклад на неделе
        session[week_key] = True
        cost = 0
    else:
        # Проверяем монеты
        if session.get('coins', 0) < price:
            return jsonify({'success': False, 'error': 'Недостаточно монет'})
        cost = price

    # Тянем карту
    card = random.choice(TAROT_CARDS)

    # Генерируем интерпретацию по теме
    interpretations = {
        'love': f"❤️ В отношениях: {card['meaning']}",
        'money': f"💰 В деньгах: {card['meaning']}",
        'future': f"🔮 В будущем: {card['meaning']}",
        'thoughts': f"💭 Он думает: {card['meaning']}",
        'yesno': f"❓ Ответ: {'Да ✨' if card['id'] % 2 == 0 else 'Нет 🌙'}"
    }

    interpretation = interpretations.get(topic, card['meaning'])

    # Списываем монеты если платно
    if cost > 0:
        session['coins'] = session.get('coins', 0) - cost

    # Добавляем карту в коллекцию
    collected = session.get('collected_cards', [])
    if card['id'] not in collected:
        collected.append(card['id'])
        session['collected_cards'] = collected

    return jsonify({
        'success': True,
        'card': card,
        'topic': topic,
        'interpretation': interpretation,
        'coins': session.get('coins', 0),
        'cost': cost
    })


@app.route('/api/add-coins', methods=['POST'])
def add_coins():
    """Добавление монет (для теста)"""
    init_user_session()
    data = request.json
    amount = data.get('amount', 10)
    session['coins'] = session.get('coins', 0) + amount
    return jsonify({
        'success': True,
        'coins': session['coins']
    })


# ============= ЗАПУСК =============

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)

from flask import Flask, render_template, session, jsonify
from datetime import datetime
import random
import os

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'dev-key-12345')

# Данные
ENERGIES = [
    "🔥 Высокая энергия",
    "💧 Спокойная энергия", 
    "🌪 Нестабильная энергия",
    "⛰ Устойчивая энергия",
    "✨ Творческая энергия"
]

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

CARDS = [
    {"id": 1, "name": "Шут", "meaning": "Новое начало, спонтанность"},
    {"id": 2, "name": "Маг", "meaning": "Сила воли, мастерство"},
    {"id": 3, "name": "Верховная Жрица", "meaning": "Интуиция, тайна"},
    {"id": 4, "name": "Императрица", "meaning": "Изобилие, плодородие"},
]

@app.route('/')
def today():
    """Главный экран 'Сегодня'"""
    
    # Инициализация сессии
    if 'coins' not in session:
        session['coins'] = 50
    if 'collected_cards' not in session:
        session['collected_cards'] = []
    
    # Проверяем, заходил ли сегодня
    today_str = datetime.now().strftime('%Y-%m-%d')
    last_visit = session.get('last_visit')
    
    daily_bonus = False
    if last_visit != today_str:
        session['coins'] = session.get('coins', 0) + 10
        session['last_visit'] = today_str
        daily_bonus = True
    
    # Данные для отображения
    context = {
        'daily_bonus': daily_bonus,
        'coins': session.get('coins', 0),
        'energy': random.choice(ENERGIES),
        'horoscope': HOROSCOPES.get('aries'),
        'card_of_day': session.get('card_of_day'),
        'collected': len(session.get('collected_cards', [])),
        'total_cards': 78,
        'now': datetime.now()
    }
    
    return render_template('today.html', **context)

@app.route('/draw-card', methods=['POST'])
def draw_card():
    """Вытянуть карту дня"""
    
    # Инициализация сессии если нужно
    if 'collected_cards' not in session:
        session['collected_cards'] = []
    if 'coins' not in session:
        session['coins'] = 50
    
    # Выбираем случайную карту
    card = random.choice(CARDS)
    session['card_of_day'] = card
    
    # Добавляем в коллекцию
    collected = session.get('collected_cards', [])
    if card['id'] not in collected:
        collected.append(card['id'])
        session['collected_cards'] = collected
        session['coins'] = session.get('coins', 0) + 5
    
    return jsonify({
        'success': True,
        'card': card,
        'coins': session['coins']
    })

@app.route('/health')
def health():
    return {"status": "ok"}

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)from flask import Flask, render_template, session, jsonify
from datetime import datetime
import random
import os

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'dev-key-12345')

# Данные
ENERGIES = [
    "🔥 Высокая энергия",
    "💧 Спокойная энергия", 
    "🌪 Нестабильная энергия",
    "⛰ Устойчивая энергия",
    "✨ Творческая энергия"
]

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

CARDS = [
    {"id": 1, "name": "Шут", "meaning": "Новое начало, спонтанность"},
    {"id": 2, "name": "Маг", "meaning": "Сила воли, мастерство"},
    {"id": 3, "name": "Верховная Жрица", "meaning": "Интуиция, тайна"},
    {"id": 4, "name": "Императрица", "meaning": "Изобилие, плодородие"},
]

@app.route('/')
def today():
    """Главный экран 'Сегодня'"""
    
    # Инициализация сессии
    if 'coins' not in session:
        session['coins'] = 50  # Стартовые монеты
    
    # Проверяем, заходил ли сегодня
    today_str = datetime.now().strftime('%Y-%m-%d')
    last_visit = session.get('last_visit')
    
    daily_bonus = False
    if last_visit != today_str:
        # Новый день - даем +10 монет
        session['coins'] = session.get('coins', 0) + 10
        session['last_visit'] = today_str
        daily_bonus = True
    
    # Данные для отображения
    context = {
        'daily_bonus': daily_bonus,
        'coins': session.get('coins', 0),
        'energy': random.choice(ENERGIES),
        'horoscope': HOROSCOPES.get('aries'),  # По умолчанию Овен
        'card_of_day': session.get('card_of_day'),
        'collected': len(session.get('collected_cards', [])),
        'total_cards': 78
    }
    
    return render_template('today.html', **context)

@app.route('/draw-card', methods=['POST'])
def draw_card():
    """Вытянуть карту дня"""
    
    # Выбираем случайную карту
    card = random.choice(CARDS)
    session['card_of_day'] = card
    
    # Добавляем в коллекцию
    collected = session.get('collected_cards', [])
    if card['id'] not in collected:
        collected.append(card['id'])
        session['collected_cards'] = collected
        # +5 монет за новую карту
        session['coins'] = session.get('coins', 0) + 5
    
    return jsonify({
        'success': True,
        'card': card,
        'coins': session['coins']
    })

@app.route('/health')
def health():
    return {"status": "ok"}

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)


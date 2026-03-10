import logging
from flask import Flask, render_template, jsonify, request, session
from datetime import datetime, timedelta
import random
import json
import os

# Настройка логирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'dev-key-12345')

# ============= ДАННЫЕ =============

# Карты Таро (78 карт)
TAROT_CARDS = [
    {"id": 0, "name": "Шут", "image": "fool.jpg", "meaning": "Новое начало, спонтанность"},
    {"id": 1, "name": "Маг", "image": "magician.jpg", "meaning": "Сила воли, мастерство"},
    # ... остальные 76 карт
]

# Энергии дня
ENERGIES = ["🔥 Высокая", "💧 Спокойная", "🌪 Нестабильная", "⛰ Устойчивая", "✨ Творческая"]

# Гороскопы для знаков зодиака
HOROSCOPES = {
    "aries": "♈ Овен: Сегодня звезды благосклонны к новым начинаниям",
    "taurus": "♉ Телец: День подходит для финансовых решений",
    # ... остальные знаки
}

# ============= МАРШРУТЫ =============

@app.route('/')
def index():
    """Входная точка - перенаправляем на today или приветствие"""
    if 'user_id' not in session:
        return render_template('index.html')
    return render_template('today.html', active='today')

@app.route('/today')
def today():
    """Главный экран 'Сегодня'"""
    # Проверяем, заходил ли сегодня пользователь
    last_visit = session.get('last_visit')
    today_str = datetime.now().strftime('%Y-%m-%d')
    
    if last_visit != today_str:
        # Новый день - даем монеты за вход
        session['coins'] = session.get('coins', 0) + 10
        session['last_visit'] = today_str
        session['daily_bonus'] = True
    
    # Получаем данные для отображения
    context = {
        'active': 'today',
        'card_of_day': session.get('card_of_day'),
        'energy': random.choice(ENERGIES),  # В реальности будет по дате
        'horoscope': HOROSCOPES.get(session.get('zodiac', 'aries')),
        'coins': session.get('coins', 0),
        'daily_bonus': session.get('daily_bonus', False)
    }
    
    return render_template('today.html', **context)

@app.route('/tarot')
def tarot():
    """Раздел Таро"""
    return render_template('tarot.html', active='tarot')

@app.route('/card-of-day')
def card_of_day():
    """Карта дня"""
    return render_template('card_of_day.html', active='tarot')

@app.route('/collection')
def collection():
    """Коллекция карт"""
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
    return render_template('quick.html', active='tarot')

@app.route('/deep-spreads')
def deep_spreads():
    """Глубокие расклады"""
    return render_template('deep.html', active='tarot')

# ============= API =============

@app.route('/api/draw-card', methods=['POST'])
def draw_card():
    """Тянет случайную карту"""
    card = random.choice(TAROT_CARDS)
    
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
    data = request.json
    card_id = data.get('card_id')
    
    # Проверяем монеты
    if session.get('coins', 0) < 50:  # Цена за глубокий расклад
        return jsonify({'success': False, 'error': 'Недостаточно монет'})
    
    # Списываем монеты
    session['coins'] = session.get('coins', 0) - 50
    
    # Генерируем глубокую интерпретацию
    deep_meaning = f"Подробное значение карты #{card_id}..."
    
    return jsonify({
        'success': True,
        'meaning': deep_meaning,
        'coins': session['coins']
    })

@app.route('/api/check-subscription')
def check_subscription():
    """Проверка подписки пользователя"""
    # В реальности здесь проверка через Telegram Payments
    return jsonify({
        'has_subscription': session.get('has_subscription', False)
    })

# ============= ЗАПУСК =============

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)

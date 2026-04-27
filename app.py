from flask import Flask, render_template, session, jsonify, request
from datetime import datetime
import random
import os

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'dev-key-12345')

# ============= ПЕРЕВОДЫ =============

TRANSLATIONS = {
    'ru': {
        'app_name': '✨ Мистика',
        'today': 'Сегодня',
        'greeting': 'Сегодня для тебя',
        'card_of_day': '🔮 Карта дня',
        'energy_of_day': '🌙 Энергия дня',
        'horoscope': '♈ Гороскоп дня',
        'quick_compatibility': '❤️ Быстрая совместимость',
        'not_opened': 'Не открыта',
        'tap_to_see': 'Нажми для просмотра',
        'quick_spread': 'Быстрый расклад',
        'your_card': 'Твоя карта дня',
        'draw_new_card': '🔄 Вытянуть новую карту (+5 монет)',
        'draw_card': '🎴 Вытянуть карту дня (+5 монет)',
        'card_collection': '📚 Коллекция карт',
        'coins': '🪙 Монет',
        'daily_bonus': '✨ +10 монет за вход! ✨',
        'energy_title': '🌙 Энергия дня',
        'energy_recommendations': 'Сегодня твоя энергия располагает к:',
        'rec1': 'Медитации и спокойствию',
        'rec2': 'Творческим начинаниям',
        'rec3': 'Общению с близкими',
        'horoscope_title': '♈ Гороскоп дня',
        'compatibility_title': '❤️ Быстрая совместимость',
        'enter_name': 'Введи имя или знак зодиака:',
        'check': 'Узнать',
        'perfect_match': '✨ Отличная совместимость! Вы дополняете друг друга.',
        'good_match': '💫 Хорошая совместимость, есть над чем работать.',
        'harmonic': '🌟 Гармоничный союз, много общего.',
        'complex': '💔 Сложная совместимость, но возможна.',
        'ideal': '💝 Идеальная совместимость! Вы созданы друг для друга.',
        'select_language': 'Выберите язык / Choose language / Selecciona idioma'
    },
    'en': {
        'app_name': '✨ Mystic',
        'today': 'Today',
        'greeting': 'Today for you',
        'card_of_day': '🔮 Card of the Day',
        'energy_of_day': '🌙 Energy of the Day',
        'horoscope': '♈ Horoscope',
        'quick_compatibility': '❤️ Quick Compatibility',
        'not_opened': 'Not opened',
        'tap_to_see': 'Tap to see',
        'quick_spread': 'Quick spread',
        'your_card': 'Your card of the day',
        'draw_new_card': '🔄 Draw new card (+5 coins)',
        'draw_card': '🎴 Draw card of the day (+5 coins)',
        'card_collection': '📚 Card Collection',
        'coins': '🪙 Coins',
        'daily_bonus': '✨ +10 coins for login! ✨',
        'energy_title': '🌙 Energy of the Day',
        'energy_recommendations': 'Today your energy is good for:',
        'rec1': 'Meditation and calm',
        'rec2': 'Creative endeavors',
        'rec3': 'Communication with loved ones',
        'horoscope_title': '♈ Horoscope',
        'compatibility_title': '❤️ Quick Compatibility',
        'enter_name': 'Enter name or zodiac sign:',
        'check': 'Check',
        'perfect_match': '✨ Perfect match! You complement each other.',
        'good_match': '💫 Good compatibility, room for growth.',
        'harmonic': '🌟 Harmonious union, much in common.',
        'complex': '💔 Complex compatibility, but possible.',
        'ideal': '💝 Ideal compatibility! Made for each other.',
        'select_language': 'Select language'
    },
    'es': {
        'app_name': '✨ Mística',
        'today': 'Hoy',
        'greeting': 'Hoy para ti',
        'card_of_day': '🔮 Carta del Día',
        'energy_of_day': '🌙 Energía del Día',
        'horoscope': '♈ Horóscopo',
        'quick_compatibility': '❤️ Compatibilidad Rápida',
        'not_opened': 'No abierta',
        'tap_to_see': 'Toca para ver',
        'quick_spread': 'Tirada rápida',
        'your_card': 'Tu carta del día',
        'draw_new_card': '🔄 Nueva carta (+5 monedas)',
        'draw_card': '🎴 Carta del día (+5 monedas)',
        'card_collection': '📚 Colección de Cartas',
        'coins': '🪙 Monedas',
        'daily_bonus': '✨ ¡+10 monedas por entrar! ✨',
        'energy_title': '🌙 Energía del Día',
        'energy_recommendations': 'Hoy tu energía es propicia para:',
        'rec1': 'Meditación y calma',
        'rec2': 'Proyectos creativos',
        'rec3': 'Comunicación con seres queridos',
        'horoscope_title': '♈ Horóscopo',
        'compatibility_title': '❤️ Compatibilidad Rápida',
        'enter_name': 'Ingresa nombre o signo zodiacal:',
        'check': 'Verificar',
        'perfect_match': '✨ ¡Compatibilidad perfecta! Se complementan.',
        'good_match': '💫 Buena compatibilidad, hay potencial.',
        'harmonic': '🌟 Unión armónica, mucho en común.',
        'complex': '💔 Compatibilidad compleja, pero posible.',
        'ideal': '💝 ¡Compatibilidad ideal! Hechos el uno para el otro.',
        'select_language': 'Seleccionar idioma'
    }
}

# Данные (оставляем как есть)
ENERGIES = {
    'ru': [
        "🔥 Высокая энергия",
        "💧 Спокойная энергия", 
        "🌪 Нестабильная энергия",
        "⛰ Устойчивая энергия",
        "✨ Творческая энергия"
    ],
    'en': [
        "🔥 High Energy",
        "💧 Calm Energy", 
        "🌪 Unstable Energy",
        "⛰ Stable Energy",
        "✨ Creative Energy"
    ],
    'es': [
        "🔥 Alta Energía",
        "💧 Energía Calma", 
        "🌪 Energía Inestable",
        "⛰ Energía Estable",
        "✨ Energía Creativa"
    ]
}

HOROSCOPES = {
    'ru': {
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
    },
    'en': {
        "aries": "♈ Aries: The stars favor new beginnings",
        "taurus": "♉ Taurus: Good day for financial decisions",
        "gemini": "♊ Gemini: Communication brings luck",
        "cancer": "♋ Cancer: Listen to your intuition",
        "leo": "♌ Leo: Your day to shine",
        "virgo": "♍ Virgo: Pay attention to details",
        "libra": "♎ Libra: Find balance",
        "scorpio": "♏ Scorpio: Transformation",
        "sagittarius": "♐ Sagittarius: Adventure awaits",
        "capricorn": "♑ Capricorn: Persistence pays off",
        "aquarius": "♒ Aquarius: New ideas",
        "pisces": "♓ Pisces: Go with the flow"
    },
    'es': {
        "aries": "♈ Aries: Las estrellas favorecen nuevos comienzos",
        "taurus": "♉ Tauro: Buen día para decisiones financieras",
        "gemini": "♊ Géminis: La comunicación trae suerte",
        "cancer": "♋ Cáncer: Escucha tu intuición",
        "leo": "♌ Leo: Tu día para brillar",
        "virgo": "♍ Virgo: Atención a los detalles",
        "libra": "♎ Libra: Encuentra el equilibrio",
        "scorpio": "♏ Escorpio: Transformación",
        "sagittarius": "♐ Sagitario: Aventura espera",
        "capricorn": "♑ Capricornio: La perseverancia paga",
        "aquarius": "♒ Acuario: Nuevas ideas",
        "pisces": "♓ Piscis: Fluye con la corriente"
    }
}

CARDS = [
    {"id": 1, "name": {"ru": "Шут", "en": "Fool", "es": "Loco"}, "meaning": {"ru": "Новое начало, спонтанность", "en": "New beginning, spontaneity", "es": "Nuevo comienzo, espontaneidad"}},
    {"id": 2, "name": {"ru": "Маг", "en": "Magician", "es": "Mago"}, "meaning": {"ru": "Сила воли, мастерство", "en": "Willpower, mastery", "es": "Fuerza de voluntad, maestría"}},
    {"id": 3, "name": {"ru": "Верховная Жрица", "en": "High Priestess", "es": "Suma Sacerdotisa"}, "meaning": {"ru": "Интуиция, тайна", "en": "Intuition, mystery", "es": "Intuición, misterio"}},
    {"id": 4, "name": {"ru": "Императрица", "en": "Empress", "es": "Emperatriz"}, "meaning": {"ru": "Изобилие, плодородие", "en": "Abundance, fertility", "es": "Abundancia, fertilidad"}},
]

# ============= ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ =============

def get_text(key, lang=None):
    """Получить текст на нужном языке"""
    if lang is None:
        lang = session.get('language', 'ru')
    return TRANSLATIONS.get(lang, TRANSLATIONS['ru']).get(key, key)

def get_energy(lang=None):
    """Получить энергию на нужном языке"""
    if lang is None:
        lang = session.get('language', 'ru')
    return random.choice(ENERGIES.get(lang, ENERGIES['ru']))

def get_horoscope(sign='aries', lang=None):
    """Получить гороскоп на нужном языке"""
    if lang is None:
        lang = session.get('language', 'ru')
    return HOROSCOPES.get(lang, HOROSCOPES['ru']).get(sign, "")

# ============= МАРШРУТЫ =============

@app.route('/')
def today():
    """Главный экран 'Сегодня'"""
    
    # Инициализация сессии
    if 'coins' not in session:
        session['coins'] = 50
    if 'collected_cards' not in session:
        session['collected_cards'] = []
    if 'language' not in session:
        session['language'] = 'ru'
    
    # Проверяем, заходил ли сегодня
    today_str = datetime.now().strftime('%Y-%m-%d')
    last_visit = session.get('last_visit')
    
    daily_bonus = False
    if last_visit != today_str:
        session['coins'] = session.get('coins', 0) + 10
        session['last_visit'] = today_str
        daily_bonus = True
    
    lang = session.get('language', 'ru')
    
    # Данные для отображения
    context = {
        'daily_bonus': daily_bonus,
        'coins': session.get('coins', 0),
        'energy': get_energy(lang),
        'horoscope': get_horoscope('aries', lang),
        'card_of_day': session.get('card_of_day'),
        'collected': len(session.get('collected_cards', [])),
        'total_cards': 78,
        'now': datetime.now(),
        'lang': lang,
        'get_text': get_text  # Передаем функцию в шаблон
    }
    
    return render_template('today.html', **context)

@app.route('/set-language', methods=['POST'])
def set_language():
    """Установка языка"""
    data = request.json
    lang = data.get('language', 'ru')
    if lang in ['ru', 'en', 'es']:
        session['language'] = lang
        return jsonify({'success': True, 'language': lang})
    return jsonify({'success': False, 'error': 'Invalid language'})

@app.route('/draw-card', methods=['POST'])
def draw_card():
    """Вытянуть карту дня"""
    
    # Инициализация сессии если нужно
    if 'collected_cards' not in session:
        session['collected_cards'] = []
    if 'coins' not in session:
        session['coins'] = 50
    if 'language' not in session:
        session['language'] = 'ru'
    
    lang = session.get('language', 'ru')
    
    # Выбираем случайную карту
    card = random.choice(CARDS)
    
    # Создаем карту с переводом
    translated_card = {
        'id': card['id'],
        'name': card['name'].get(lang, card['name']['ru']),
        'meaning': card['meaning'].get(lang, card['meaning']['ru'])
    }
    
    session['card_of_day'] = translated_card
    
    # Добавляем в коллекцию
    collected = session.get('collected_cards', [])
    if card['id'] not in collected:
        collected.append(card['id'])
        session['collected_cards'] = collected
        session['coins'] = session.get('coins', 0) + 5
    
    return jsonify({
        'success': True,
        'card': translated_card,
        'coins': session['coins']
    })

@app.route('/health')
def health():
    return {"status": "ok"}

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)

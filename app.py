@app.route('/api/quick-spread', methods=['POST'])
def quick_spread():
    """Быстрый расклад по теме"""
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
        'love': f"В отношениях вас ждет {card['meaning'].lower()}",
        'money': f"В финансовых вопросах {card['meaning'].lower()}",
        'future': f"В ближайшем будущем {card['meaning'].lower()}",
        'thoughts': f"Он думает о вас: {card['meaning'].lower()}",
        'yesno': f"Ответ: {'Да' if card['id'] % 2 == 0 else 'Нет'}"
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

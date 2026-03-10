import os
import logging
from flask import Flask
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
import threading
import time

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Токен из переменных окружения
BOT_TOKEN = os.environ.get('8617082336:AAGnOPuLaL6HBclu16ZnW-9UYcNTh1NdeBo')
logger.info(f"Токен загружен: {'✅' if BOT_TOKEN else '❌'}")

# Flask приложение
app = Flask(__name__)

@app.route('/')
def home():
    return "✅ Бот работает! Статус: OK"

@app.route('/health')
def health():
    return {
        "status": "ok",
        "bot_token_set": bool(BOT_TOKEN),
        "time": str(time.time())
    }

# Простейший обработчик
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    logger.info(f"✅ ПОЛУЧЕНА КОМАНДА START от пользователя {user.id} (@{user.username})")
    await update.message.reply_text(
        f"👋 Привет, {user.first_name}!\n\n"
        f"✅ Бот работает правильно!\n"
        f"🆔 Твой ID: {user.id}"
    )

def run_bot():
    """Запуск бота в отдельном потоке"""
    if not BOT_TOKEN:
        logger.error("❌ НЕТ ТОКЕНА!")
        return
    
    max_retries = 3
    for attempt in range(max_retries):
        try:
            logger.info(f"🟡 Попытка {attempt + 1}/{max_retries} запустить бота...")
            
            # Создаем приложение с правильными параметрами
            app_bot = Application.builder().token(BOT_TOKEN).build()
            app_bot.add_handler(CommandHandler("start", start))
            
            logger.info("✅ Бот создан, запускаем polling...")
            
            # Запускаем бота (этот метод блокирующий)
            app_bot.run_polling(allowed_updates=['message'], drop_pending_updates=True)
            
            # Если дошли сюда - бот работает
            break
            
        except Exception as e:
            logger.error(f"❌ Ошибка при запуске бота (попытка {attempt + 1}): {e}")
            if attempt < max_retries - 1:
                logger.info("Ждем 5 секунд перед следующей попыткой...")
                time.sleep(5)
            else:
                logger.error("❌ Все попытки запустить бота провалились")

# Запускаем бота в отдельном потоке
if BOT_TOKEN:
    logger.info("🟡 Создаем поток для бота...")
    bot_thread = threading.Thread(target=run_bot, daemon=True)
    bot_thread.start()
    logger.info("✅ Поток для бота создан и запущен")
    
    # Даем боту время на запуск
    time.sleep(2)
    logger.info("🟢 Бот должен быть запущен")
else:
    logger.error("❌ Токен не найден - бот не запущен!")

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 10000))
    logger.info(f"🚀 Запуск Flask на порту {port}")
    app.run(host='0.0.0.0', port=port)

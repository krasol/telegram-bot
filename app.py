import os
import logging
from flask import Flask
from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext
import threading
import time

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Токен (вы можете оставить его здесь для теста, но лучше использовать переменные окружения)
BOT_TOKEN = "8617082336:AAGnOPuLaL6HBclu16ZnW-9UYcNTh1NdeBo"
logger.info(f"Токен загружен: ✅")

# Flask приложение
app = Flask(__name__)

@app.route('/')
def home():
    return "✅ Бот на Render работает (версия с Updater)!"

@app.route('/health')
def health():
    return {"status": "ok", "bot_running": True}

# Обработчик команды /start для старой версии (Updater)
def start(update: Update, context: CallbackContext):
    user = update.effective_user
    logger.info(f"✅ Команда START от {user.first_name} (ID: {user.id})")
    update.message.reply_text(
        f"👋 Привет, {user.first_name}!\n\n"
        f"✅ Бот работает на Render через Updater!\n"
        f"🆔 Твой ID: {user.id}"
    )

def run_bot():
    """Запуск бота с использованием Updater (стабильная версия)"""
    try:
        logger.info("🟡 Запускаем бота (версия с Updater)...")

        # Создаем Updater
        updater = Updater(token=BOT_TOKEN, use_context=True)
        dispatcher = updater.dispatcher

        # Добавляем обработчик
        dispatcher.add_handler(CommandHandler("start", start))

        logger.info("✅ Бот создан, запускаем polling...")
        updater.start_polling()
        logger.info("✅ Бот успешно запущен и слушает команды!")

        # Держим поток живым
        while True:
            time.sleep(10)

    except Exception as e:
        logger.error(f"❌ Ошибка бота: {e}")

# Запускаем бота в фоне
logger.info("🟡 Создаем поток для бота...")
bot_thread = threading.Thread(target=run_bot, daemon=True)
bot_thread.start()
time.sleep(3)
logger.info("✅ Поток для бота создан и запущен")

if __name__ == "__main__":
    # ВАЖНО ДЛЯ RENDER: используем PORT из окружения
    port = int(os.environ.get('PORT', 10000))
    logger.info(f"🚀 Запуск Flask на порту {port}")
    app.run(host='0.0.0.0', port=port)

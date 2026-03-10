import asyncio
import logging
from flask import Flask
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
import threading
import time
import sys
import os

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Токен
BOT_TOKEN = "8617082336:AAGnOPuLaL6HBclu16ZnW-9UYcNTh1NdeBo"
logger.info(f"Токен загружен: ✅")

# Flask приложение
app = Flask(__name__)


@app.route('/')
def home():
    return "✅ Бот работает локально!"


@app.route('/health')
def health():
    return {"status": "ok", "message": "Bot is running"}


# Асинхронный обработчик
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    logger.info(f"✅ Команда START от {user.first_name} (ID: {user.id})")
    await update.message.reply_text(
        f"👋 Привет, {user.first_name}!\n\n"
        f"✅ Бот работает локально!\n"
        f"🆔 Твой ID: {user.id}\n"
        f"📅 Время: {time.strftime('%H:%M:%S')}"
    )


def run_bot():
    """Запуск бота в отдельном потоке с asyncio"""
    try:
        logger.info("🟡 Запускаем бота...")
        
        # Создаем и настраиваем приложение
        application = Application.builder().token(BOT_TOKEN).build()
        application.add_handler(CommandHandler("start", start))
        
        logger.info("✅ Бот настроен, запускаем polling...")
        
        # Создаем новый цикл событий для потока
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        # Запускаем бота через asyncio
        loop.run_until_complete(initialize_and_start(application))
        
    except Exception as e:
        logger.error(f"❌ Ошибка бота: {e}")
        if "Conflict" in str(e):
            logger.error("❌ Конфликт! Возможно бот уже запущен в другом окне")
            logger.info("💡 Закройте все другие терминалы с ботом и запустите снова")


async def initialize_and_start(application):
    """Инициализация и запуск бота"""
    try:
        await application.initialize()
        await application.start()
        
        logger.info("✅ Бот запущен и готов к работе!")
        
        # Запускаем polling
        await application.updater.start_polling(drop_pending_updates=True)
        
        # Держим бота запущенным
        while True:
            await asyncio.sleep(1)
            
    except asyncio.CancelledError:
        logger.info("🟡 Получен сигнал остановки...")
    finally:
        # Останавливаем бота корректно
        await application.updater.stop()
        await application.stop()
        await application.shutdown()


# Функция для запуска Flask
def run_flask():
    app.run(host='127.0.0.1', port=5000, debug=False, use_reloader=False)


if __name__ == "__main__":
    logger.info("🟡 Создаем поток для бота...")
    bot_thread = threading.Thread(target=run_bot, daemon=True)
    bot_thread.start()
    
    # Даем боту время запуститься
    time.sleep(3)
    logger.info("✅ Бот запущен! Отправь /start в Telegram")
    
    # Запускаем Flask в отдельном потоке (опционально)
    flask_thread = threading.Thread(target=run_flask, daemon=True)
    flask_thread.start()
    
    logger.info("🚀 Запуск Flask на http://127.0.0.1:5000")
    
    # Держим главный поток активным
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("🟡 Получен сигнал прерывания, останавливаем бота...")
        sys.exit(0)

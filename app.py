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
    return "✅ Бот работает на Render!"


@app.route('/health')
def health():
    return {"status": "ok", "message": "Bot is running"}


# Асинхронный обработчик
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    logger.info(f"✅ Команда START от {user.first_name} (ID: {user.id})")
    await update.message.reply_text(
        f"👋 Привет, {user.first_name}!\n\n"
        f"✅ Бот работает на Render!\n"
        f"🆔 Твой ID: {user.id}"
    )


def run_bot():
    """Запуск бота в отдельном потоке с обработкой ошибок Python 3.14"""
    try:
        logger.info("🟡 Запускаем бота в потоке...")
        
        # Создаем новый цикл событий
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        # Запускаем бота
        loop.run_until_complete(run_bot_async())
        
    except Exception as e:
        logger.error(f"❌ Ошибка бота: {e}")
        import traceback
        traceback.print_exc()


async def run_bot_async():
    """Асинхронный запуск бота с альтернативным методом"""
    try:
        logger.info("🟡 Создание приложения бота...")
        
        # Альтернативный способ создания приложения
        application = (
            Application.builder()
            .token(BOT_TOKEN)
            .build()
        )
        
        # Добавляем обработчик
        application.add_handler(CommandHandler("start", start))
        
        logger.info("✅ Бот настроен, запускаем polling...")
        
        # Используем другой метод запуска
        await application.initialize()
        await application.start()
        
        # Запускаем polling вручную
        await application.updater.start_polling()
        
        logger.info("✅ Бот успешно запущен!")
        
        # Держим бота запущенным
        while True:
            await asyncio.sleep(10)
            
    except Exception as e:
        logger.error(f"❌ Ошибка при работе бота: {e}")
        import traceback
        traceback.print_exc()


# Запускаем бота при импорте
logger.info("🟡 Инициализация приложения...")

# Даем небольшую задержку перед запуском бота
time.sleep(2)

try:
    bot_thread = threading.Thread(target=run_bot, daemon=True)
    bot_thread.start()
    logger.info("✅ Поток бота создан и запущен!")
except Exception as e:
    logger.error(f"❌ Ошибка при создании потока бота: {e}")

# Для локального запуска
if __name__ == "__main__":
    logger.info("🚀 Локальный запуск Flask...")
    app.run(host='127.0.0.1', port=5000, debug=True)

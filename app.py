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

# Токен (лучше использовать переменные окружения на Render)
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


async def run_bot_async():
    """Асинхронный запуск бота"""
    try:
        # Создаем приложение
        application = Application.builder().token(BOT_TOKEN).build()
        application.add_handler(CommandHandler("start", start))
        
        logger.info("✅ Бот настроен, запускаем polling...")
        
        # Запускаем бота (этот метод сам управляет циклом событий)
        await application.run_polling(drop_pending_updates=True)
        
    except Exception as e:
        logger.error(f"❌ Ошибка бота: {e}")
        import traceback
        traceback.print_exc()


def run_bot():
    """Запуск бота в отдельном потоке"""
    try:
        logger.info("🟡 Запускаем бота в потоке...")
        asyncio.run(run_bot_async())
    except Exception as e:
        logger.error(f"❌ Ошибка в потоке бота: {e}")


# !!! ВАЖНО: Запускаем бота ПРИ ИМПОРТЕ модуля (когда gunicorn загружает app)
logger.info("🟡 Инициализация приложения - запускаем бота...")
bot_thread = threading.Thread(target=run_bot, daemon=True)
bot_thread.start()
logger.info("✅ Бот запущен в фоновом потоке!")


# Этот блок выполняется только при локальном запуске
if __name__ == "__main__":
    logger.info("🚀 Локальный запуск Flask...")
    app.run(host='127.0.0.1', port=5000, debug=True)

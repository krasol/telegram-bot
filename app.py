import os
import logging
import sys
from flask import Flask
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
import threading
import asyncio

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
logger.info(f"Python version: {sys.version}")

# Токен
BOT_TOKEN = "8617082336:AAGnOPuLaL6HBclu16ZnW-9UYcNTh1NdeBo"
logger.info(f"Токен загружен: ✅")

# Flask приложение
app = Flask(__name__)

@app.route('/')
def home():
    return "✅ Бот работает на Python 3.14!"

@app.route('/health')
def health():
    return {
        "status": "ok",
        "python": sys.version.split()[0],
        "bot_token": "✅"
    }

# Асинхронный обработчик для новой версии
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    logger.info(f"✅ Команда START от {user.first_name} (ID: {user.id})")
    await update.message.reply_text(
        f"👋 Привет, {user.first_name}!\n\n"
        f"✅ Бот работает на Python 3.14!\n"
        f"🆔 Твой ID: {user.id}\n"
        f"📦 Версия: python-telegram-bot 20.7"
    )

def run_bot():
    """Запуск бота"""
    try:
        logger.info("🟡 Запускаем бота (версия 20.7)...")
        
        # Создаем приложение
        application = Application.builder().token(BOT_TOKEN).build()
        application.add_handler(CommandHandler("start", start))
        
        logger.info("✅ Бот создан, запускаем polling...")
        
        # Запускаем
        application.run_polling(drop_pending_updates=True)
        
    except Exception as e:
        logger.error(f"❌ Ошибка бота: {e}")

# Запускаем бота в фоне
logger.info("🟡 Создаем поток для бота...")
bot_thread = threading.Thread(target=run_bot, daemon=True)
bot_thread.start()
time.sleep(3)
logger.info("✅ Поток для бота создан")

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 10000))
    logger.info(f"🚀 Запуск Flask на порту {port}")
    app.run(host='0.0.0.0', port=port)

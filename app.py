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

# ⚠️ ТОКЕН ПРЯМО В КОДЕ (НЕБЕЗОПАСНО!)
BOT_TOKEN = "8617082336:AAGnOPuLaL6HBclu16ZnW-9UYcNTh1NdeBo"
logger.info(f"Токен загружен из кода: ✅")

# Flask приложение
app = Flask(__name__)

@app.route('/')
def home():
    return "✅ Бот работает! Токен в коде"

@app.route('/health')
def health():
    return {
        "status": "ok", 
        "bot_token_set": True,
        "token_source": "hardcoded_in_code"
    }

# Простейший обработчик
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    logger.info(f"✅ ПОЛУЧЕНА КОМАНДА START от пользователя {user.id}")
    await update.message.reply_text(
        f"👋 Привет, {user.first_name}!\n\n"
        f"✅ Бот работает с токеном в коде!\n"
        f"🆔 Твой ID: {user.id}"
    )

def run_bot():
    """Запуск бота в отдельном потоке"""
    try:
        logger.info("🟡 Запускаем бота...")
        app_bot = Application.builder().token(BOT_TOKEN).build()
        app_bot.add_handler(CommandHandler("start", start))
        logger.info("✅ Бот запущен и готов к работе!")
        app_bot.run_polling()
    except Exception as e:
        logger.error(f"❌ Ошибка бота: {e}")

# Запускаем бота в фоне
logger.info("🟡 Создаем поток для бота...")
bot_thread = threading.Thread(target=run_bot, daemon=True)
bot_thread.start()
logger.info("✅ Поток для бота создан и запущен")

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 10000))
    logger.info(f"🚀 Запуск Flask на порту {port}")
    app.run(host='0.0.0.0', port=port)

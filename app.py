import os
import logging
import sys
import time
import threading
from flask import Flask
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
logger.info(f"Python version: {sys.version}")

BOT_TOKEN = "8617082336:AAGnOPuLaL6HBclu16ZnW-9UYcNTh1NdeBo"
logger.info(f"Токен загружен: ✅")

app = Flask(__name__)

@app.route('/')
def home():
    return "✅ Бот работает!"

@app.route('/health')
def health():
    return {"status": "ok"}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    logger.info(f"✅ Команда START от {user.first_name}")
    await update.message.reply_text(f"👋 Привет, {user.first_name}!")

def run_bot():
    try:
        logger.info("🟡 Запускаем бота...")
        # ⚠️ ВНИМАНИЕ: ТОЛЬКО ТАК ДЛЯ 20.7
        application = Application.builder().token(BOT_TOKEN).build()
        application.add_handler(CommandHandler("start", start))
        logger.info("✅ Бот создан, запускаем polling...")
        application.run_polling()
    except Exception as e:
        logger.error(f"❌ Ошибка бота: {e}")

logger.info("🟡 Создаем поток...")
bot_thread = threading.Thread(target=run_bot, daemon=True)
bot_thread.start()
time.sleep(3)
logger.info("✅ Поток создан")

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)

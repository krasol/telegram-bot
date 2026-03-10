import os
import logging
from flask import Flask
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
from threading import Thread

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Токен из переменных окружения (НЕ ВСТАВЛЯЙТЕ СЮДА ТОКЕН!)
BOT_TOKEN = os.environ.get('BOT_TOKEN')
logger.info(f"Токен загружен: {'✅' if BOT_TOKEN else '❌'}")

# Если нет токена - пишем ошибку но продолжаем
if not BOT_TOKEN:
    logger.error("❌ ТОКЕН НЕ НАЙДЕН! Добавьте BOT_TOKEN в переменные окружения на Render!")

# Flask приложение
app = Flask(__name__)

@app.route('/')
def home():
    token_status = "✅" if BOT_TOKEN else "❌"
    return f"Бот работает! Статус токена: {token_status}"

@app.route('/health')
def health():
    return {
        "status": "ok",
        "bot_token_set": bool(BOT_TOKEN)
    }

# Простейший обработчик
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    logger.info(f"❗ ПОЛУЧЕНА КОМАНДА START от пользователя {user.id}")
    await update.message.reply_text(f"Привет, {user.first_name}! Я работаю!")

def run_bot():
    """Запуск бота"""
    if not BOT_TOKEN:
        logger.error("❌ НЕТ ТОКЕНА - бот не запущен!")
        return
    
    try:
        logger.info("🟡 Запускаем бота...")
        app_bot = Application.builder().token(BOT_TOKEN).build()
        app_bot.add_handler(CommandHandler("start", start))
        logger.info("✅ Бот запущен и готов к работе!")
        app_bot.run_polling()
    except Exception as e:
        logger.error(f"❌ Ошибка бота: {e}")

# Запускаем бота в фоне
if BOT_TOKEN:
    logger.info("🟡 Создаем поток для бота...")
    bot_thread = Thread(target=run_bot)
    bot_thread.daemon = True
    bot_thread.start()
    logger.info("✅ Поток создан")
else:
    logger.error("❌ Бот НЕ запущен - нет токена!")

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)

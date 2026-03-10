import logging
from flask import Flask, request, jsonify, send_from_directory
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from telegram.ext import Application, CommandHandler, ContextTypes
import threading
import asyncio
import os

# Настройка логирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Токен бота
BOT_TOKEN = "8617082336:AAGnOPuLaL6HBclu16ZnW-9UYcNTh1NdeBo"

# Flask приложение для Mini App и API
app = Flask(__name__, static_folder='static', static_url_path='/static')

# ============= МАРШРУТЫ ДЛЯ MINI APP =============

@app.route('/')
def index():
    """Главная страница Mini App"""
    return send_from_directory('.', 'index.html')

@app.route('/app')
def mini_app():
    """Страница Mini App"""
    return send_from_directory('.', 'app.html')

@app.route('/api/data')
def get_data():
    """API для передачи данных в Mini App"""
    return jsonify({
        "message": "Данные из бота",
        "status": "ok"
    })

@app.route('/health')
def health():
    return {"status": "ok", "bot": "running", "mini_app": "active"}

# ============= ЛОГИКА БОТА =============

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Отправляет кнопку для открытия Mini App"""
    user = update.effective_user
    
    # URL вашего Mini App (на том же сервере)
    web_app_url = "https://telegram-bot-amkh.onrender.com/app"
    
    # Создаем кнопку для открытия Mini App
    keyboard = [[
        InlineKeyboardButton(
            text="🚀 Открыть Mini App", 
            web_app=WebAppInfo(url=web_app_url)
        )
    ]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        f"👋 Привет, {user.first_name}!\n\n"
        f"Нажми кнопку ниже, чтобы открыть Mini App:",
        reply_markup=reply_markup
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда помощи"""
    await update.message.reply_text(
        "🔹 /start - открыть Mini App\n"
        "🔹 /help - это сообщение"
    )

# ============= ЗАПУСК БОТА В ФОНЕ =============

def run_bot():
    """Запуск бота в отдельном потоке"""
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        application = Application.builder().token(BOT_TOKEN).build()
        application.add_handler(CommandHandler("start", start))
        application.add_handler(CommandHandler("help", help_command))
        
        logger.info("✅ Бот настроен, запускаем...")
        application.run_polling(drop_pending_updates=True)
    except Exception as e:
        logger.error(f"❌ Ошибка бота: {e}")

# Запускаем бота при старте
logger.info("🟡 Запуск бота в фоновом потоке...")
bot_thread = threading.Thread(target=run_bot, daemon=True)
bot_thread.start()
logger.info("✅ Бот запущен!")

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 10000)))

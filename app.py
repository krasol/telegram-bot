import os
import logging
import asyncio
from flask import Flask, send_from_directory
from telegram import Update, WebAppInfo, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from dotenv import load_dotenv

# Загружаем переменные окружения
load_dotenv()

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Конфигурация
TOKEN = os.environ.get('8617082336:AAGnOPuLaL6HBclu16ZnW-9UYcNTh1NdeBo')
# URL вашего приложения на Render (будет доступен после деплоя)
# Формат: https://название-приложения.onrender.com
APP_URL = os.environ.get('RENDER_EXTERNAL_URL', 'https://telegram-mini-app.onrender.com')

# Создаем Flask приложение для хостинга веб-приложения
app = Flask(__name__, static_folder='web_app')

@app.route('/')
def serve_index():
    """Главная страница веб-приложения"""
    return send_from_directory('web_app', 'index.html')

@app.route('/<path:path>')
def serve_static(path):
    """Статические файлы (CSS, JS)"""
    return send_from_directory('web_app', path)

@app.route('/health')
def health():
    """Проверка здоровья для Render"""
    return {"status": "ok"}, 200

# Функции для Telegram бота
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /start"""
    user = update.effective_user
    
    # Создаем клавиатуру с кнопкой для открытия Mini App
    keyboard = [[
        InlineKeyboardButton(
            "🚀 Открыть мини-приложение", 
            web_app=WebAppInfo(url=APP_URL)
        )
    ]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    welcome_text = (
        f"👋 Привет, {user.first_name}!\n\n"
        f"🎮 Это демонстрационное Telegram Mini App\n"
        f"✅ Работает на Render.com\n\n"
        f"Нажми кнопку ниже, чтобы открыть приложение:"
    )
    
    await update.message.reply_text(welcome_text, reply_markup=reply_markup)

async def web_app_data(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка данных от Web App"""
    if update.message and update.message.web_app_data:
        data = update.message.web_app_data.data
        logger.info(f"Получены данные: {data}")
        
        await update.message.reply_text(
            f"✅ Данные получены!\n"
            f"Вы отправили: {data}"
        )

async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Простой эхо-обработчик"""
    await update.message.reply_text(f"Вы написали: {update.message.text}")

async def run_bot():
    """Запуск Telegram бота"""
    if not TOKEN:
        logger.error("Токен бота не найден!")
        return
    
    # Создаем приложение бота
    application = Application.builder().token(TOKEN).build()
    
    # Добавляем обработчики
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.StatusUpdate.WEB_APP_DATA, web_app_data))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))
    
    # Запускаем бота
    logger.info("Бот запущен...")
    await application.run_polling()

if __name__ == '__main__':
    # Запускаем Flask сервер для веб-приложения
    port = int(os.environ.get('PORT', 10000))
    
    # В отдельном потоке запускаем бота
    import threading
    bot_thread = threading.Thread(target=lambda: asyncio.run(run_bot()))
    bot_thread.daemon = True
    bot_thread.start()
    
    # Запускаем Flask
    logger.info(f"Flask сервер запущен на порту {port}")
    app.run(host='0.0.0.0', port=port)

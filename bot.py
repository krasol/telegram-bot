import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from telegram.ext import Application, CommandHandler, ContextTypes

# Настройка логирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Токен вашего бота
BOT_TOKEN = "8617082336:AAGnOPuLaL6HBclu16ZnW-9UYcNTh1NdeBo"

# URL вашего сайта на Render
WEB_APP_URL = "https://telegram-bot-1-ddfa.onrender.com"


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Отправляет кнопку для открытия Mini App"""
    user = update.effective_user

    # Создаем кнопку с WebApp
    keyboard = [[
        InlineKeyboardButton(
            text="🚀 Открыть Mini App",
            web_app=WebAppInfo(url=WEB_APP_URL)
        )
    ]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        f"👋 Привет, {user.first_name}!\n\n"
        f"Нажми кнопку, чтобы открыть Mini App:",
        reply_markup=reply_markup
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда помощи"""
    await update.message.reply_text(
        "🔹 /start - открыть Mini App\n"
        "🔹 /help - это сообщение"
    )


def main():
    """Запуск бота на ПК"""
    try:
        # Создаем приложение
        application = Application.builder().token(BOT_TOKEN).build()

        # Добавляем обработчики
        application.add_handler(CommandHandler("start", start))
        application.add_handler(CommandHandler("help", help_command))

        logger.info("✅ Бот запущен на ПК!")
        logger.info(f"🌐 Mini App URL: {WEB_APP_URL}")

        # Запускаем бота
        application.run_polling(drop_pending_updates=True)

    except Exception as e:
        logger.error(f"❌ Ошибка: {e}")


if __name__ == "__main__":
    main()
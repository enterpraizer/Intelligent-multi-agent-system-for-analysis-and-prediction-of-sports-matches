# --- src/bot/bot_main.py ---
from telegram.ext import ApplicationBuilder
from src.bot.handlers import register_handlers

TOKEN = '8144016399:AAF_Ww1EJXRNQPMlAzPq1jE2ni40dm9o94s'  # вставь токен своего бота

def main():
    # Создание приложения (бота)
    app = ApplicationBuilder().token(TOKEN).build()

    # Регистрируем хэндлеры
    register_handlers(app)

    # Запуск бота
    print("Бот запущен...")
    app.run_polling()

if __name__ == '__main__':
    main()

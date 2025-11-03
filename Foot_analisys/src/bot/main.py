"""
Главный файл запуска Telegram бота
"""
import sys
import os

# Добавляем корень проекта в путь
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
sys.path.insert(0, PROJECT_ROOT)

import logging
from telegram.ext import ApplicationBuilder
from src.bot.handlers import register_handlers

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join(PROJECT_ROOT, 'logs/bot.log')),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

# ТВОЙ ТОКЕН БОТА
TOKEN = '8144016399:AAF_Ww1EJXRNQPMlAzPq1jE2ni40dm9o94s'


def main():
    """Запуск бота"""
    logger.info("Запуск бота...")

    # Создание приложения
    app = ApplicationBuilder().token(TOKEN).build()

    # Регистрируем хэндлеры
    register_handlers(app)

    logger.info("✅ Бот запущен и готов к работе!")
    logger.info("Доступные команды:")
    logger.info("  /start - Приветствие")
    logger.info("  /next_match - Сделать прогноз")
    logger.info("  /teams - Список команд")
    logger.info("  /status - Статус системы")

    # Запуск бота
    app.run_polling()


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        logger.info("Бот остановлен пользователем")
    except Exception as e:
        logger.error(f"Критическая ошибка: {e}", exc_info=True)
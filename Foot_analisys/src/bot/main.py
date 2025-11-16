"""
Главный файл запуска Telegram бота
"""
import atexit
import sys
import os
import asyncio

from Foot_analisys.src.bot.services.notification_service import NotificationService

# Добавляем корень проекта в путь
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
sys.path.insert(0, PROJECT_ROOT)

import logging
from telegram.ext import ApplicationBuilder
from Foot_analisys.src.bot.handlers import register_all_handlers
from Foot_analisys.src.bot.handlers.main_handler import register_main_handler

# Создаем папку для логов если её нет
LOGS_DIR = os.path.join(PROJECT_ROOT, 'logs')
os.makedirs(LOGS_DIR, exist_ok=True)

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join(LOGS_DIR, 'bot.log')),
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

    # Инициализация сервиса уведомлений
    global notification_service
    notification_service = NotificationService(app)

    # Регистрируем все обработчики
    register_all_handlers(app)
    register_main_handler(app)

    # Запуск планировщика уведомлений
    app.job_queue.run_once(
        lambda context: asyncio.create_task(notification_service.start_scheduler()),
        5
    )

    logger.info("✅ Бот запущен и готов к работе!")
    logger.info("Доступные команды:")
    logger.info("  /start - Главное меню")
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
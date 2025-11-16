"""
Базовые обработчики команд
"""
from telegram.ext import CommandHandler, CallbackQueryHandler
from Foot_analisys.src.bot.handlers.menu_handlers import show_main_menu

# /start - главное меню
async def start(update, context):
    """Команда /start - показывает главное меню"""
    await show_main_menu(update, context)

# /next_match - перенаправление в меню прогнозов
async def next_match(update, context):
    """Старая команда /next_match - перенаправляем в меню прогнозов"""
    await show_main_menu(update, context)

def register_base_handlers(app):
    """Регистрирует базовые обработчики команд"""
    app.add_handler(CommandHandler('start', start))
    app.add_handler(CommandHandler('next_match', next_match))
"""
Пакет обработчиков бота
"""
from .base_handlers import register_base_handlers
from .menu_handlers import register_menu_handlers
from .prediction_handlers import register_prediction_handlers
from .schedule_handlers import register_schedule_handlers
from .user_handlers import register_user_handlers
from .stats_handlers import register_stats_handlers
from .favorites_handlers import register_favorites_handlers

def register_all_handlers(app):
    """Регистрирует все обработчики"""
    register_base_handlers(app)
    register_menu_handlers(app)
    register_prediction_handlers(app)
    register_schedule_handlers(app)
    register_user_handlers(app)
    register_stats_handlers(app)
    register_favorites_handlers(app)
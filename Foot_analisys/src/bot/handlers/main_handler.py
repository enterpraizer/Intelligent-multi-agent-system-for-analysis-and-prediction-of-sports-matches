"""
Главный обработчик кнопок - маршрутизатор
"""
from telegram import Update
from telegram.ext import ContextTypes, CallbackQueryHandler, MessageHandler, filters

from Foot_analisys.src.bot.handlers.about_handlers import show_about_menu, refresh_system_data, show_system_status
from Foot_analisys.src.bot.handlers.favorites_handlers import show_favorites_menu, clear_favorites, toggle_favorite_team
from Foot_analisys.src.bot.handlers.menu_handlers import (
    show_main_menu, show_stats_menu, show_settings_menu, show_prediction_menu
)
from Foot_analisys.src.bot.handlers.schedule_handlers import (
    show_schedule_menu, show_upcoming_matches, show_schedule_leagues, show_league_schedule
)
from Foot_analisys.src.bot.handlers.prediction_handlers import (
    start_quick_prediction, start_detailed_prediction, start_llm_prediction,
    show_league_matches_for_quick_prediction, show_league_matches_for_detailed_prediction,
    process_match_selection, save_user_prediction_handler, show_league_matches_for_llm_prediction, process_llm_analysis
)
from Foot_analisys.src.bot.handlers.settings_handlers import show_notifications_settings, toggle_notifications, \
    set_notification_time
from Foot_analisys.src.bot.handlers.user_handlers import show_prediction_history
from Foot_analisys.src.bot.handlers.stats_handlers import (
    show_team_stats_menu, show_popular_teams, start_team_search,
    show_team_stats, handle_team_search, show_all_teams, show_teams_by_league, handle_league_page
)

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Главный обработчик нажатий на инлайн-кнопки"""
    query = update.callback_query
    await query.answer()

    data = query.data

    # Главное меню и подменю
    if data == "main_menu":
        await show_main_menu(update, context)

    elif data == "menu_stats":
        await show_stats_menu(update, context)

    elif data == "menu_settings":
        await show_settings_menu(update, context)

    elif data == "menu_schedule":
        await show_schedule_menu(update, context)

    elif data == "menu_prediction":
        await show_prediction_menu(update, context)

    elif data == "history_predictions":
        await show_prediction_history(update, context)

    # Расписание
    elif data == "schedule_upcoming":
        await show_upcoming_matches(update, context)

    elif data == "schedule_leagues":
        await show_schedule_leagues(update, context)

    elif data.startswith('schedule_league_'):
        await show_league_schedule(update, context)

    # Прогнозы
    elif data == "prediction_quick":
        await start_quick_prediction(update, context)

    elif data == "prediction_detailed":
        await start_detailed_prediction(update, context)

    elif data == "prediction_llm":
        await start_llm_prediction(update, context)

    # Быстрый прогноз (из расписания)
    elif data.startswith('quick_league_'):
        await show_league_matches_for_quick_prediction(update, context)

    # Детальный прогноз (из расписания)
    elif data.startswith('detailed_league_'):
        await show_league_matches_for_detailed_prediction(update, context)

    # Выбор матча для быстрого прогноза
    elif data.startswith('quick_match_'):
        await process_match_selection(update, context, 'quick')

    # Выбор матча для детального прогноза
    elif data.startswith('detailed_match_'):
        await process_match_selection(update, context, 'detailed')

    # Статистика команд
    elif data == "stats_team":
        await show_team_stats_menu(update, context)

    elif data == "stats_popular":
        await show_popular_teams(update, context)

    elif data == "stats_search":
        await start_team_search(update, context)

    elif data.startswith('stats_team_'):
        await show_team_stats(update, context)

    elif data == "stats_all":
        await show_all_teams(update, context)

    elif data == "settings_favorites":
        await show_favorites_menu(update, context)

    elif data == "favorites_clear":
        await clear_favorites(update, context)

    elif data.startswith('favorite_toggle_'):
        await toggle_favorite_team(update, context)

    # В button_handler добавить:
    elif data == "settings_notifications":
        await show_notifications_settings(update, context)

    elif data == "notifications_toggle":
        await toggle_notifications(update, context)

    elif data.startswith('notifications_time_'):
        await set_notification_time(update, context)

    elif data == "prediction_llm":
        await start_llm_prediction(update, context)

    elif data.startswith('llm_league_'):
        await show_league_matches_for_llm_prediction(update, context)

    elif data.startswith('llm_match_'):
        await process_llm_analysis(update, context)

    elif data == "menu_about":
        await show_about_menu(update, context)

    elif data == "refresh_system":
        await refresh_system_data(update, context)

    elif data == "system_status":
        await show_system_status(update, context)

    elif data.startswith('stats_league_') and '_page_' not in data:
        await show_teams_by_league(update, context)

    elif data.startswith('stats_league_') and '_page_' in data:
        await handle_league_page(update, context)

    elif data.startswith('save_quick_') or data.startswith('save_detailed_'):
        await save_user_prediction_handler(update, context)

    elif data in ["stats_player", "stats_h2h",
                  "settings_favorites", "settings_notifications",
                  "schedule_search", "menu_about", "stats_all"]:
        await query.edit_message_text(
            f"🛠️ <b>Функция в разработке</b>\n\n"
            f"Раздел '{data}' находится в стадии разработки.\n"
            f"Следите за обновлениями!",
            parse_mode='HTML'
        )

def register_main_handler(app):
    """Регистрирует главный обработчик кнопок и сообщений"""
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_team_search))
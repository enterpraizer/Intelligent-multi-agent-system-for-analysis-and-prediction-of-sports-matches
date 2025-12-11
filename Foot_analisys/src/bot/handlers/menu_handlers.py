"""
Обработчики меню и навигации
"""
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes

async def show_main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показ главного меню"""
    keyboard = [
        [InlineKeyboardButton("📊 Статистика", callback_data="menu_stats")],
        [InlineKeyboardButton("⭐ Мои настройки", callback_data="menu_settings")],
        [InlineKeyboardButton("📅 Расписание матчей", callback_data="menu_schedule")],
        [InlineKeyboardButton("🎯 Прогноз матча", callback_data="menu_prediction")],
        [InlineKeyboardButton("📈 История прогнозов", callback_data="history_predictions")],
        [InlineKeyboardButton("ℹ️ О боте", callback_data="menu_about")]
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    if update.callback_query:
        await update.callback_query.edit_message_text(
            "🏠 <b>Главное меню</b>\n\n"
            "Выберите раздел:",
            reply_markup=reply_markup,
            parse_mode='HTML'
        )
    else:
        await update.message.reply_text(
            "🏠 <b>Главное меню</b>\n\n"
            "Выберите раздел:",
            reply_markup=reply_markup,
            parse_mode='HTML'
        )

async def show_stats_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Меню статистики"""
    keyboard = [
        [InlineKeyboardButton("📈 Статистика команды", callback_data="stats_team")],
        [InlineKeyboardButton("👤 Статистика игрока", callback_data="stats_player")],
        [InlineKeyboardButton("🆚 История личных встреч", callback_data="stats_h2h")],
        [InlineKeyboardButton("🔙 Назад", callback_data="main_menu")]
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.callback_query.edit_message_text(
        "📊 <b>Раздел статистики</b>\n\n"
        "Выберите тип статистики:",
        reply_markup=reply_markup,
        parse_mode='HTML'
    )


async def show_settings_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Меню настроек и избранного"""
    from Foot_analisys.src.bot.utils.user_data import get_user_data

    user_data = get_user_data(update.callback_query.from_user.id)

    favorite_text = ""
    if user_data['favorite_teams']:
        favorite_count = len(user_data['favorite_teams'])
        favorite_names = [team['name'] for team in user_data['favorite_teams'][:3]]
        favorite_text = f"\n⭐ Избранные команды: {', '.join(favorite_names)}"
        if favorite_count > 3:
            favorite_text += f" ... (всего {favorite_count})"
    else:
        favorite_text = "\n⭐ Избранные команды: не выбраны"

    notification_status = "✅ Включены" if user_data['notifications']['enabled'] else "❌ Выключены"
    notification_time = user_data['notifications']['time_before_match']

    keyboard = [
        [InlineKeyboardButton("⭐ Избранные команды", callback_data="settings_favorites")],
        [InlineKeyboardButton("🔔 Уведомления", callback_data="settings_notifications")],
        [InlineKeyboardButton("🔙 Назад", callback_data="main_menu")]
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.callback_query.edit_message_text(
        f"⭐ <b>Мои настройки</b>\n\n"
        f"{favorite_text}\n"
        f"🔔 Уведомления: {notification_status}\n"
        f"⏰ Время уведомлений: за {notification_time} часов до матча",
        reply_markup=reply_markup,
        parse_mode='HTML'
    )

async def show_prediction_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Меню прогнозов"""
    keyboard = [
        [InlineKeyboardButton("⚡ Быстрый прогноз", callback_data="prediction_quick")],
        [InlineKeyboardButton("📊 Детальный прогноз", callback_data="prediction_detailed")],
        [InlineKeyboardButton("🤖 Прогноз LLM", callback_data="prediction_llm")],
        [InlineKeyboardButton("🔙 Назад", callback_data="main_menu")]
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.callback_query.edit_message_text(
        "🎯 <b>Прогноз матча</b>\n\n"
        "Выберите тип прогноза:\n\n"
        "⚡ <b>Быстрый прогноз</b> - выбрать из расписания, только счет\n"
        "📊 <b>Детальный прогноз</b> - выбрать из расписания, полная статистика\n"
        "🤖 <b>Прогноз LLM</b> - расширенный анализ с ИИ",
        reply_markup=reply_markup,
        parse_mode='HTML'
    )

def register_menu_handlers(app):
    """Регистрирует обработчики меню"""
    pass
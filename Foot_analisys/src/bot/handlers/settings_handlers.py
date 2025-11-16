# handlers/settings_handlers.py - новый файл
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes
from Foot_analisys.src.bot.utils.user_data import get_user_data


async def show_notifications_settings(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Настройки уведомлений"""
    user_id = update.callback_query.from_user.id
    user_data = get_user_data(user_id)
    notifications = user_data['notifications']

    status_icon = "✅" if notifications['enabled'] else "❌"
    time_options = [1, 3, 6, 12, 24]  # часы до матча

    keyboard = [
        [InlineKeyboardButton(
            f"{status_icon} Уведомления: {'Вкл' if notifications['enabled'] else 'Выкл'}",
            callback_data="notifications_toggle"
        )],
    ]

    # Кнопки времени уведомлений
    time_row = []
    for hours in time_options:
        is_active = "🟢" if notifications['time_before_match'] == hours else "⚪"
        time_row.append(InlineKeyboardButton(
            f"{is_active}{hours}ч",
            callback_data=f"notifications_time_{hours}"
        ))
        if len(time_row) == 3:  # 3 кнопки в ряд
            keyboard.append(time_row)
            time_row = []
    if time_row:
        keyboard.append(time_row)

    keyboard.append([InlineKeyboardButton("🔙 Назад", callback_data="menu_settings")])

    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.callback_query.edit_message_text(
        f"🔔 <b>Настройки уведомлений</b>\n\n"
        f"Получать уведомления о матчах избранных команд:\n"
        f"• Текущая настройка: за <b>{notifications['time_before_match']} часов</b> до матча\n\n"
        f"Выберите время уведомления:",
        reply_markup=reply_markup,
        parse_mode='HTML'
    )


async def toggle_notifications(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Включение/выключение уведомлений"""
    user_id = update.callback_query.from_user.id
    user_data = get_user_data(user_id)

    user_data['notifications']['enabled'] = not user_data['notifications']['enabled']

    await update.callback_query.answer(
        f"Уведомления {'включены' if user_data['notifications']['enabled'] else 'выключены'}"
    )
    await show_notifications_settings(update, context)


async def set_notification_time(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Установка времени уведомления"""
    user_id = update.callback_query.from_user.id
    hours = int(update.callback_query.data.split('_')[2])

    user_data = get_user_data(user_id)
    user_data['notifications']['time_before_match'] = hours

    await update.callback_query.answer(f"Уведомления за {hours} часов до матча")
    await show_notifications_settings(update, context)
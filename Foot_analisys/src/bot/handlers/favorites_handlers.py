"""
Обработчики избранных команд
"""
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes, CallbackQueryHandler
from Foot_analisys.src.bot.utils.user_data import (
    add_favorite_team, remove_favorite_team,
    get_favorite_teams, is_team_favorite
)
from Foot_analisys.src.bot.services.team_stats_service import team_stats_service
import logging

logger = logging.getLogger(__name__)


async def show_favorites_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Меню избранных команд"""
    user_id = update.callback_query.from_user.id
    favorite_teams = get_favorite_teams(user_id)

    if not favorite_teams:
        keyboard = [
            [InlineKeyboardButton("➕ Добавить команды", callback_data="stats_team")],
            [InlineKeyboardButton("🔙 Назад", callback_data="menu_settings")]
        ]

        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.callback_query.edit_message_text(
            "⭐ <b>Избранные команды</b>\n\n"
            "У вас пока нет избранных команд.\n\n"
            "Вы можете добавить команды через раздел статистики.",
            reply_markup=reply_markup,
            parse_mode='HTML'
        )
        return

    # Создаем список избранных команд
    keyboard = []
    for i in range(0, len(favorite_teams), 2):
        row = []
        team1 = favorite_teams[i]
        row.append(InlineKeyboardButton(team1['name'], callback_data=f"stats_team_{team1['id']}"))

        if i + 1 < len(favorite_teams):
            team2 = favorite_teams[i + 1]
            row.append(InlineKeyboardButton(team2['name'], callback_data=f"stats_team_{team2['id']}"))

        keyboard.append(row)

    # Кнопки управления
    keyboard.extend([
        [InlineKeyboardButton("🗑️ Удалить избранные", callback_data="favorites_clear")],
        [InlineKeyboardButton("➕ Добавить ещё", callback_data="stats_team")],
        [InlineKeyboardButton("🔙 Назад", callback_data="menu_settings")]
    ])

    reply_markup = InlineKeyboardMarkup(keyboard)

    teams_list = "\n".join([f"• {team['name']}" for team in favorite_teams])

    await update.callback_query.edit_message_text(
        f"⭐ <b>Избранные команды</b>\n\n"
        f"Ваши избранные команды ({len(favorite_teams)}):\n\n"
        f"{teams_list}\n\n"
        f"Выберите команду для просмотра статистики:",
        reply_markup=reply_markup,
        parse_mode='HTML'
    )


async def clear_favorites(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Очистка всех избранных команд"""
    user_id = update.callback_query.from_user.id
    user_data = get_favorite_teams(user_id)

    if not user_data:
        await update.callback_query.edit_message_text(
            "❌ <b>Нет избранных команд</b>\n\n"
            "У вас нет избранных команд для удаления.",
            parse_mode='HTML'
        )
        return

    # Очищаем список избранных
    context.user_data['favorite_teams'] = []

    keyboard = [
        [InlineKeyboardButton("➕ Добавить команды", callback_data="stats_team")],
        [InlineKeyboardButton("🔙 Назад", callback_data="menu_settings")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.callback_query.edit_message_text(
        "✅ <b>Избранные команды очищены</b>\n\n"
        "Все команды удалены из избранного.",
        reply_markup=reply_markup,
        parse_mode='HTML'
    )


async def toggle_favorite_team(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Добавление/удаление команды из избранного"""
    query = update.callback_query
    user_id = query.from_user.id

    # Получаем team_id из callback_data (формат: favorite_toggle_{team_id})
    team_id = int(query.data.split('_')[2])

    # Получаем информацию о команде
    team_info = team_stats_service.get_team_info(team_id)
    team_name = team_info.get('name', 'Неизвестная команда')

    # Проверяем, есть ли команда уже в избранном
    if is_team_favorite(user_id, team_id):
        # Удаляем из избранного
        remove_favorite_team(user_id, team_id)
        action_text = "❌ Удалена из избранного"
        new_button_text = "⭐ Добавить в избранное"
    else:
        # Добавляем в избранное
        add_favorite_team(user_id, team_id, team_name)
        action_text = "✅ Добавлена в избранное"
        new_button_text = "❌ Удалить из избранного"

    # Обновляем сообщение
    await query.answer(f"{team_name} {action_text}")

    # Обновляем кнопку в сообщении со статистикой
    try:
        # Получаем текущее сообщение
        message_text = query.message.text
        message_markup = query.message.reply_markup

        # Создаем новую клавиатуру с обновленной кнопкой
        new_keyboard = []
        for row in message_markup.inline_keyboard:
            new_row = []
            for button in row:
                if button.callback_data == query.data:
                    # Заменяем кнопку избранного
                    new_row.append(InlineKeyboardButton(
                        new_button_text,
                        callback_data=f"favorite_toggle_{team_id}"
                    ))
                else:
                    new_row.append(button)
            new_keyboard.append(new_row)

        new_reply_markup = InlineKeyboardMarkup(new_keyboard)

        # Обновляем сообщение
        await query.edit_message_reply_markup(new_reply_markup)

    except Exception as e:
        logger.error(f"Ошибка обновления кнопки избранного: {e}")


def register_favorites_handlers(app):
    """Регистрирует обработчики избранных команд"""
    # Обработчики регистрируются через CallbackQueryHandler в главном файле
    pass
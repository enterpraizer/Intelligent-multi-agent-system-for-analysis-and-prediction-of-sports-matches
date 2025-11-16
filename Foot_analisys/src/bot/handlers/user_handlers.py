"""
Обработчики пользовательских данных
"""
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes
from Foot_analisys.src.bot.utils.user_data import get_user_data


async def show_prediction_history(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """История пользовательских прогнозов"""
    user_id = update.callback_query.from_user.id
    user_data = get_user_data(user_id)

    if not user_data['user_predictions']:
        text = "📈 <b>История ваших прогнозов</b>\n\n"
        text += "У вас пока нет сохраненных прогнозов.\n"
        text += "После получения прогноза от бота вы сможете оставить свой вариант!"
    else:
        text = "📈 <b>История ваших прогнозов</b>\n\n"

        # Статистика точности
        total = len(user_data['user_predictions'])
        correct = sum(1 for p in user_data['user_predictions'] if p.get('is_correct') is True)
        accuracy = (correct / total) * 100 if total > 0 else 0

        text += f"📊 Общая точность: <b>{accuracy:.1f}%</b> ({correct}/{total})\n\n"

        # Последние 3 прогноза
        text += "Последние прогнозы:\n"
        for pred in user_data['user_predictions'][-3:]:
            text += f"• {pred['home_team']} vs {pred['away_team']}\n"
            text += f"  Ваш прогноз: {pred['user_prediction']}\n"
            if pred['actual_score']:
                status = "✅" if pred['is_correct'] else "❌"
                text += f"  Результат: {pred['actual_score']} {status}\n"
            else:
                text += f"  ⏳ Ожидание матча\n"
            text += "\n"

    keyboard = [[InlineKeyboardButton("🔙 Назад", callback_data="main_menu")]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.callback_query.edit_message_text(
        text,
        reply_markup=reply_markup,
        parse_mode='HTML'
    )


def register_user_handlers(app):
    """Регистрирует обработчики пользовательских данных"""
    # Обработчики пользовательских данных регистрируются через CallbackQueryHandler
    pass
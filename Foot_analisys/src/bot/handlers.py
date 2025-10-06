from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import CommandHandler, CallbackQueryHandler, ContextTypes
from src.bot.messages import START_MESSAGE, NEXT_MATCH_MESSAGE, REPORT_MESSAGE

# Пример списка матчей
matches = [
{"id": 1, "home_team": "Команда А", "away_team": "Команда Б", "date": "2025-10-05"},
{"id": 2, "home_team": "Команда C", "away_team": "Команда D", "date": "2025-10-06"},
]

# /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(START_MESSAGE)

# /next_match
async def next_match(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = []
    for match in matches:
        text = f"{match['home_team']} vs {match['away_team']} ({match['date']})"
        keyboard.append([InlineKeyboardButton(text, callback_data=str(match['id']))])
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(NEXT_MATCH_MESSAGE, reply_markup=reply_markup)

# Выбор кнопки
async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    match_id = int(query.data)
    selected_match = next((m for m in matches if m['id'] == match_id), None)
    if selected_match:
        report_text = (
        f"{REPORT_MESSAGE}\n"
        f"{selected_match['home_team']} vs {selected_match['away_team']} ({selected_match['date']})\n"
        f"Прогноз: Победа {selected_match['home_team']} 2:1"
        )
        await query.edit_message_text(report_text)

# Регистрация хэндлеров
def register_handlers(app):
    app.add_handler(CommandHandler('start', start))
    app.add_handler(CommandHandler('next_match', next_match))
    app.add_handler(CallbackQueryHandler(button))
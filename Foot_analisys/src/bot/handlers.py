"""
Telegram bot handlers с интеграцией координатора агентов
"""
import sys
import os

from scipy.stats.contingency import margins

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import CommandHandler, CallbackQueryHandler, ContextTypes
from src.bot.messages import START_MESSAGE, NEXT_MATCH_MESSAGE, REPORT_MESSAGE
from src.coordinator.coordinator import MatchCoordinator
import logging

logger = logging.getLogger(__name__)

# Инициализация координатора (один раз при запуске бота)
coordinator = MatchCoordinator(
    use_llm=False
)

# Глобальная инициализация
COORDINATOR_READY = False


def init_coordinator():
    """Инициализация координатора при старте бота"""
    global COORDINATOR_READY
    if not COORDINATOR_READY:
        logger.info("Инициализация координатора...")
        if coordinator.initialize():
            COORDINATOR_READY = True
            logger.info("✅ Координатор готов")
        else:
            logger.error("❌ Ошибка инициализации координатора")
    return COORDINATOR_READY


# /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда /start"""
    await update.message.reply_text(START_MESSAGE, parse_mode='HTML')


# /next_match - показывает список команд для выбора матча
async def next_match(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда /next_match - выбор команд для прогноза"""

    # Инициализируем координатор если нужно
    if not init_coordinator():
        await update.message.reply_text("❌ Ошибка инициализации системы. Попробуйте позже.")
        return

    # Получаем список всех команд
    leagues = coordinator.get_league_list()


    if not leagues:
        await update.message.reply_text("❌ Нет данных о лигах в базе.")
        return

    # Сохраняем список команд в контексте пользователя
    context.user_data['leagues'] = leagues
    context.user_data['step'] = 'select_league'

    # Создаем кнопки для выбора домашней команды
    keyboard = []
    for i in range(0, len(leagues), 2):  # По 2 кнопки в ряд
        row = []
        row.append(InlineKeyboardButton(leagues[i], callback_data=f"league_{i}"))
        if i + 1 < len(leagues):
            row.append(InlineKeyboardButton(leagues[i + 1], callback_data=f"league_{i + 1}"))
        keyboard.append(row)

    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "🏠 Выберите лигу:",
        reply_markup=reply_markup
    )


# /teams - показать список всех команд
async def list_teams(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда /teams - показать все доступные команды"""

    if not init_coordinator():
        await update.message.reply_text("❌ Ошибка инициализации системы.")
        return

    teams = coordinator.get_team_list()

    if not teams:
        await update.message.reply_text("❌ Нет команд в базе данных.")
        return

    # Форматируем список команд
    teams_text = "📋 Доступные команды:\n\n"
    for i, team in enumerate(teams, 1):
        teams_text += f"{i}. {team}\n"

    # Телеграм ограничивает длину сообщения, разбиваем если нужно
    if len(teams_text) > 4000:
        chunks = [teams_text[i:i + 4000] for i in range(0, len(teams_text), 4000)]
        for chunk in chunks:
            await update.message.reply_text(chunk)
    else:
        await update.message.reply_text(teams_text)


# /status - статус системы
async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда /status - показать статус системы"""

    if not init_coordinator():
        await update.message.reply_text("❌ Система не инициализирована.")
        return

    status_info = coordinator.get_status()

    status_text = f"""
📊 Статус системы:

{'✅' if status_info['initialized'] else '❌'} Инициализация
{'✅' if status_info['data_loaded'] else '❌'} Данные загружены
🤖 Моделей загружено: {status_info['models_loaded']}
{'✅' if status_info['llm_enabled'] else '📝'} Генерация отчетов: {'LLM' if status_info['llm_enabled'] else 'Шаблоны'}

Команд в базе: {len(coordinator.get_team_list())}
"""

    await update.message.reply_text(status_text)


# Обработчик кнопок
async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик нажатий на инлайн-кнопки"""
    query = update.callback_query
    await query.answer()

    data = query.data
    leagues = context.user_data.get('leagues', [])
    step = context.user_data.get('step', '')

    # Выбор домашней команды
    if data.startswith('league_'):
        logger.info("huiiii")
        league_idx = int(data.split('_')[1])
        league = leagues[league_idx]

        context.user_data['league'] = league
        context.user_data['step'] = 'select_home'

        # Показываем кнопки для выбора гостевой команды
        keyboard = []
        teams = coordinator.get_team_list(league_idx)
        context.user_data['teams'] = teams
        logger.info(teams)

        for i in range(0, len(teams), 2):  # По 2 кнопки в ряд
            row = []
            row.append(InlineKeyboardButton(teams[i], callback_data=f"home_{i}"))
            if i + 1 < len(leagues):
                row.append(InlineKeyboardButton(teams[i + 1], callback_data=f"home_{i + 1}"))
            keyboard.append(row)

        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(
            f"⚽ Лига: {league}\n🏠 Выберите домашнюю команду:",
            reply_markup=reply_markup
        )
    # Выбор гостевой команды
    elif data.startswith('home_'):
        teams = context.user_data.get('teams', [])
        team_idx = int(data.split('_')[1])
        home_team = teams[team_idx]
        context.user_data['home_team'] = home_team

        keyboard = []
        for i in range(0, len(teams), 2):
            if teams[i] == home_team and (i + 1 >= len(teams) or teams[i + 1] == home_team):
                continue  # Пропускаем если обе команды = домашней

            row = []
            if teams[i] != home_team:
                row.append(InlineKeyboardButton(teams[i], callback_data=f"away_{i}"))
            if i + 1 < len(teams) and teams[i + 1] != home_team:
                row.append(InlineKeyboardButton(teams[i + 1], callback_data=f"away_{i + 1}"))

            if row:
                keyboard.append(row)

        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(
            f"🏠 Домашняя команда: {home_team}\n✈️ Выберите гостевую команду:",
            reply_markup=reply_markup
        )
    elif data.startswith('away_'):
        teams = context.user_data.get('teams', [])
        team_idx = int(data.split('_')[1])
        away_team = teams[team_idx]
        home_team = context.user_data.get('home_team')

        if not home_team:
            await query.edit_message_text("❌ Ошибка: домашняя команда не выбрана. Используйте /next_match")
            return

        # Показываем "загрузку"
        await query.edit_message_text(
            f"🏠 {home_team} vs ✈️ {away_team}\n\n⏳ Анализирую данные и строю прогноз..."
        )

        # ДЕЛАЕМ ПРОГНОЗ
        try:
            result = coordinator.predict_match(home_team, away_team)

            if result['success']:
                # Форматируем отчет для телеграма
                report = format_telegram_report(result)

                # Отправляем отчет (разбиваем если длинный)
                if len(report) > 4000:
                    chunks = [report[i:i + 4000] for i in range(0, len(report), 4000)]
                    await query.edit_message_text(chunks[0])
                    for chunk in chunks[1:]:
                        await query.message.reply_text(chunk, parse_mode='HTML')
                else:
                    await query.edit_message_text(report, parse_mode='HTML')

                # Кнопка для нового прогноза
                keyboard = [[InlineKeyboardButton("🔄 Новый прогноз", callback_data="new_prediction")]]
                reply_markup = InlineKeyboardMarkup(keyboard)
                await query.message.reply_text("Хотите сделать еще один прогноз?", reply_markup=reply_markup)

            else:
                await query.edit_message_text(
                    f"❌ Ошибка прогноза: {result.get('error', 'Неизвестная ошибка')}"
                )

        except Exception as e:
            logger.error(f"Ошибка прогноза: {e}", exc_info=True)
            await query.edit_message_text(f"❌ Произошла ошибка при создании прогноза: {str(e)}")

    # Новый прогноз
    elif data == 'new_prediction':
        await query.message.delete()
        # Имитируем команду /next_match
        leagues = coordinator.get_league_list()

        if not leagues:
            await update.message.reply_text("❌ Нет данных о лигах в базе.")
            return

        # Сохраняем список команд в контексте пользователя
        context.user_data['leagues'] = leagues
        context.user_data['step'] = 'select_league'

        # Создаем кнопки для выбора домашней команды
        keyboard = []
        for i in range(0, len(leagues), 2):  # По 2 кнопки в ряд
            row = []
            row.append(InlineKeyboardButton(leagues[i], callback_data=f"league_{i}"))
            if i + 1 < len(leagues):
                row.append(InlineKeyboardButton(leagues[i + 1], callback_data=f"league_{i + 1}"))
            keyboard.append(row)

        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.callback_query.message.reply_text(
            "🏠 Выберите лигу:",
            reply_markup=reply_markup
        )


def format_telegram_report(result: dict) -> str:
    """Форматирует отчет для Telegram (с эмодзи и читаемой структурой)"""

    predictions = result['predictions']
    home_team = result['home_team']
    away_team = result['away_team']

    home_goals = round(predictions.get('Target_FTHG', 1.5), 1)
    away_goals = round(predictions.get('Target_FTAG', 1.2), 1)
    score = f"{int(round(home_goals))}:{int(round(away_goals))}"

    # Вероятности
    goal_diff = home_goals - away_goals
    if goal_diff > 0.5:
        home_prob = min(85, 50 + goal_diff * 15)
        away_prob = max(5, 20 - goal_diff * 10)
        result_text = f"🏆 Победа {home_team}"
    elif goal_diff < -0.5:
        away_prob = min(85, 50 - goal_diff * 15)
        home_prob = max(5, 20 + goal_diff * 10)
        result_text = f"🏆 Победа {away_team}"
    else:
        home_prob = 35
        away_prob = 35
        result_text = "🤝 Ничья"

    draw_prob = 100 - home_prob - away_prob

    report = f"""
⚽️ <b>ПРОГНОЗ МАТЧА</b>

🏠 <b>{home_team}</b> vs ✈️ <b>{away_team}</b>

━━━━━━━━━━━━━━━━━━━━━━━━
🎯 <b>ОСНОВНОЙ ПРОГНОЗ</b>

<b>Счет:</b> {score}
<b>Результат:</b> {result_text}

<b>Вероятности:</b>
  🏠 Победа хозяев: {home_prob:.0f}%
  🤝 Ничья: {draw_prob:.0f}%
  ✈️ Победа гостей: {away_prob:.0f}%

━━━━━━━━━━━━━━━━━━━━━━━━
📊 <b>СТАТИСТИКА</b>

⚽️ Голы: {home_goals:.1f} - {away_goals:.1f}
🎯 Удары: {predictions.get('Target_HS', 10):.0f} - {predictions.get('Target_AS', 8):.0f}
🔵 В створ: {predictions.get('Target_HST', 4):.0f} - {predictions.get('Target_AST', 3):.0f}
🚩 Угловые: {predictions.get('Target_HC', 5):.0f} - {predictions.get('Target_AC', 4):.0f}
⚠️ Фолы: {predictions.get('Target_HF', 12):.0f} - {predictions.get('Target_AF', 11):.0f}
🟨 Желтые: {predictions.get('Target_HY', 2):.0f} - {predictions.get('Target_AY', 2):.0f}
🟥 Красные: {predictions.get('Target_HR', 0):.0f} - {predictions.get('Target_AR', 0):.0f}
"""

    # Ключевые моменты
    total_goals = home_goals + away_goals
    moments = []

    if total_goals > 3:
        moments.append(f"⚡️ Результативный матч ({total_goals:.1f} голов)")
    elif total_goals < 2:
        moments.append("🔒 Низкая результативность")

    if predictions.get('Target_HS', 0) + predictions.get('Target_AS', 0) > 20:
        moments.append("🎯 Много ударов - активная игра")

    if predictions.get('Target_HY', 0) + predictions.get('Target_AY', 0) > 4:
        moments.append("⚠️ Напряженный матч с фолами")

    if moments:
        report += "\n━━━━━━━━━━━━━━━━━━━━━━━━\n⚡️ <b>КЛЮЧЕВЫЕ МОМЕНТЫ</b>\n\n"
        report += "\n".join(moments)

    return report


# Регистрация хэндлеров
def register_handlers(app):
    """Регистрирует все обработчики команд"""
    app.add_handler(CommandHandler('start', start))
    app.add_handler(CommandHandler('next_match', next_match))
    app.add_handler(CommandHandler('teams', list_teams))
    app.add_handler(CommandHandler('status', status))
    app.add_handler(CallbackQueryHandler(button))
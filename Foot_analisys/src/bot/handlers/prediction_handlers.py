"""
Обработчики прогнозов матчей
"""
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes, CommandHandler
from Foot_analisys.src.bot.services.schedule_service import schedule_service
from Foot_analisys.src.bot.services.team_mapper import team_mapper
from Foot_analisys.src.bot.services.prediction_formatter import format_quick_prediction, format_detailed_prediction
from Foot_analisys.src.bot.utils.user_data import save_user_prediction
from Foot_analisys.src.coordinator.coordinator import MatchCoordinator
from Foot_analisys.src.bot.services.llm_analysis_service import llm_analysis_service
import logging

logger = logging.getLogger(__name__)


coordinator = MatchCoordinator(use_llm=False)
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

#Быстрый прогноз
async def start_quick_prediction(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Начало быстрого прогноза из расписания"""
    keyboard = []
    leagues = list(schedule_service.LEAGUE_IDS.keys())

    for i in range(0, len(leagues), 2):
        row = []
        row.append(InlineKeyboardButton(leagues[i], callback_data=f"quick_league_{i}"))
        if i + 1 < len(leagues):
            row.append(InlineKeyboardButton(leagues[i + 1], callback_data=f"quick_league_{i + 1}"))
        keyboard.append(row)

    keyboard.append([InlineKeyboardButton("🔙 Назад", callback_data="menu_prediction")])

    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.callback_query.edit_message_text(
        "⚡ <b>Быстрый прогноз</b>\n\n"
        "Выберите лигу из расписания:",
        reply_markup=reply_markup,
        parse_mode='HTML'
    )

#Детальный прогноз
async def start_detailed_prediction(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Начало детального прогноза из расписания"""
    keyboard = []
    leagues = list(schedule_service.LEAGUE_IDS.keys())

    for i in range(0, len(leagues), 2):
        row = []
        row.append(InlineKeyboardButton(leagues[i], callback_data=f"detailed_league_{i}"))
        if i + 1 < len(leagues):
            row.append(InlineKeyboardButton(leagues[i + 1], callback_data=f"detailed_league_{i + 1}"))
        keyboard.append(row)

    keyboard.append([InlineKeyboardButton("🔙 Назад", callback_data="menu_prediction")])

    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.callback_query.edit_message_text(
        "📊 <b>Детальный прогноз</b>\n\n"
        "Выберите лигу из расписания:",
        reply_markup=reply_markup,
        parse_mode='HTML'
    )

# Выбор конкретного матча из расписания лиги для быстрого прогноза
async def show_league_matches_for_quick_prediction(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показать матчи лиги для выбора быстрого прогноза"""
    league_idx = int(update.callback_query.data.split('_')[2])
    leagues = list(schedule_service.LEAGUE_IDS.keys())
    league_name = leagues[league_idx]

    try:
        valid_matches, invalid_matches = schedule_service.get_matches_with_valid_mapping(league_name)

        if not valid_matches:
            await update.callback_query.edit_message_text(
                f"❌ Нет доступных матчей для прогноза в {league_name}.\n"
                f"Не удалось преобразовать названия команд.",
                parse_mode='HTML'
            )
            return

        text = f"⚡ <b>Быстрый прогноз - {league_name}</b>\n\n"
        text += "Выберите матч:\n\n"

        keyboard = []
        for i, match in enumerate(valid_matches):
            button_text = f"🏠 {match['home_team']} vs ✈️ {match['away_team']}"
            callback_data = f"quick_match_{match['home_team']}_{match['away_team']}"
            keyboard.append([InlineKeyboardButton(button_text, callback_data=callback_data)])

        keyboard.append([InlineKeyboardButton("🔙 Назад", callback_data="prediction_quick")])

        reply_markup = InlineKeyboardMarkup(keyboard)

        await update.callback_query.edit_message_text(text, reply_markup=reply_markup, parse_mode='HTML')

    except Exception as e:
        logger.error(f"Ошибка получения матчей для быстрого прогноза: {e}")
        await update.callback_query.edit_message_text(
            f"❌ Ошибка при получении матчей {league_name}.",
            parse_mode='HTML'
        )

# Выбор конкретного матча из расписания лиги для детального прогноза
async def show_league_matches_for_detailed_prediction(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показать матчи лиги для выбора детального прогноза"""
    league_idx = int(update.callback_query.data.split('_')[2])
    leagues = list(schedule_service.LEAGUE_IDS.keys())
    league_name = leagues[league_idx]

    try:
        # Получаем только матчи с успешным маппингом
        valid_matches, invalid_matches = schedule_service.get_matches_with_valid_mapping(league_name)

        if not valid_matches:
            await update.callback_query.edit_message_text(
                f"❌ Нет доступных матчей для прогноза в {league_name}.\n"
                f"Не удалось преобразовать названия команд.",
                parse_mode='HTML'
            )
            return

        text = f"📊 <b>Детальный прогноз - {league_name}</b>\n\n"
        text += "Выберите матч:\n\n"

        keyboard = []
        for i, match in enumerate(valid_matches):
            button_text = f"🏠 {match['home_team']} vs ✈️ {match['away_team']}"
            callback_data = f"detailed_match_{match['home_team']}_{match['away_team']}"
            keyboard.append([InlineKeyboardButton(button_text, callback_data=callback_data)])

        keyboard.append([InlineKeyboardButton("🔙 Назад", callback_data="prediction_detailed")])

        reply_markup = InlineKeyboardMarkup(keyboard)

        await update.callback_query.edit_message_text(text, reply_markup=reply_markup, parse_mode='HTML')

    except Exception as e:
        logger.error(f"Ошибка получения матчей для детального прогноза: {e}")
        await update.callback_query.edit_message_text(
            f"❌ Ошибка при получении матчей {league_name}.",
            parse_mode='HTML'
        )

async def process_match_selection(update: Update, context: ContextTypes.DEFAULT_TYPE, prediction_type: str):
    """Обработка выбора матча для любого типа прогноза"""
    query = update.callback_query
    data = query.data

    parts = data.split('_')
    home_team = parts[2]
    away_team = parts[3]

    mapped_home, mapped_away, success, error = team_mapper.validate_mapping(home_team, away_team)

    if not success:
        await query.edit_message_text(
            f"❌ <b>Ошибка преобразования названий команд</b>\n\n"
            f"{error}\n\n"
            f"Пожалуйста, выберите другой матч.",
            parse_mode='HTML'
        )
        return

    # Сохраняем преобразованные названия команд
    context.user_data['home_team'] = mapped_home
    context.user_data['away_team'] = mapped_away
    context.user_data['original_home_team'] = home_team
    context.user_data['original_away_team'] = away_team
    context.user_data['prediction_type'] = prediction_type

    type_icon = "⚡" if prediction_type == 'quick' else "📊"
    type_name = "Быстрый прогноз" if prediction_type == 'quick' else "Детальный прогноз"

    await query.edit_message_text(
        f"{type_icon} {type_name}\n"
        f"🏠 {home_team} → {mapped_home}\n"
        f"✈️ {away_team} → {mapped_away}\n\n"
        f"⏳ Анализирую данные..."
    )

#делаем прогноз с преобразованными названиями
    try:
        if not init_coordinator():
            await query.edit_message_text("❌ Ошибка инициализации системы.")
            return

        result = coordinator.predict_match(mapped_home, mapped_away)

        if result['success']:
            if prediction_type == 'quick':
                report = format_quick_prediction(result)
            else:
                report = format_detailed_prediction(result)

            await query.edit_message_text(report, parse_mode='HTML')

            # Кнопка для сохранения пользовательского прогноза
            keyboard = [
                [InlineKeyboardButton("💾 Сохранить мой прогноз", callback_data=f"save_{prediction_type}_{mapped_home}_{mapped_away}")],
                [InlineKeyboardButton("🔄 Новый прогноз", callback_data=f"prediction_{prediction_type}")],
                [InlineKeyboardButton("🏠 Главное меню", callback_data="main_menu")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)

            score = report.split('Счет: ')[1].split('\n')[0] if 'Счет: ' in report else 'N/A'
            await query.message.reply_text(
                f"🤔 <b>Не хотите ли оставить свой прогноз?</b>\n\n"
                f"Мой прогноз: {score}",
                reply_markup=reply_markup,
                parse_mode='HTML'
            )

        else:
            await query.edit_message_text(
                f"❌ Ошибка прогноза: {result.get('error', 'Неизвестная ошибка')}"
            )

    except Exception as e:
        logger.error(f"Ошибка прогноза: {e}", exc_info=True)
        await query.edit_message_text(f"❌ Произошла ошибка при создании прогноза: {str(e)}")

async def save_user_prediction_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик сохранения пользовательского прогноза"""
    query = update.callback_query
    data = query.data

    parts = data.split('_')
    home_team = parts[2]
    away_team = parts[3]

    user_id = query.from_user.id
    save_user_prediction(user_id, home_team, away_team, "пользовательский")

    await query.edit_message_text(
        f"✅ <b>Ваш прогноз сохранен!</b>\n\n"
        f"🏠 {home_team} vs ✈️ {away_team}\n"
        f"👤 Ваш прогноз будет учтен\n\n"
        f"Просмотреть историю прогнозов можно в главном меню.",
        parse_mode='HTML'
    )


async def list_teams(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда /teams - показать все доступные команды"""
    if not init_coordinator():
        await update.message.reply_text("❌ Ошибка инициализации системы.")
        return

    teams = coordinator.get_team_list()

    if not teams:
        await update.message.reply_text("❌ Нет команд в базе данных.")
        return

    teams_text = "📋 Доступные команды:\n\n"
    for i, team in enumerate(teams, 1):
        teams_text += f"{i}. {team}\n"

    if len(teams_text) > 4000:
        chunks = [teams_text[i:i + 4000] for i in range(0, len(teams_text), 4000)]
        for chunk in chunks:
            await update.message.reply_text(chunk)
    else:
        await update.message.reply_text(teams_text)


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


async def start_llm_prediction(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Начало LLM прогноза - выбор матча из расписания"""
    keyboard = []
    leagues = list(schedule_service.LEAGUE_IDS.keys())

    for i in range(0, len(leagues), 2):
        row = []
        row.append(InlineKeyboardButton(leagues[i], callback_data=f"llm_league_{i}"))
        if i + 1 < len(leagues):
            row.append(InlineKeyboardButton(leagues[i + 1], callback_data=f"llm_league_{i + 1}"))
        keyboard.append(row)

    keyboard.append([InlineKeyboardButton("🔙 Назад", callback_data="menu_prediction")])

    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.callback_query.edit_message_text(
        "🤖 <b>Прогноз с LLM-анализом</b>\n\n"
        "Выберите лигу из расписания для глубокого анализа матча:",
        reply_markup=reply_markup,
        parse_mode='HTML'
    )


async def show_league_matches_for_llm_prediction(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показать матчи лиги для выбора LLM анализа"""
    league_idx = int(update.callback_query.data.split('_')[2])
    leagues = list(schedule_service.LEAGUE_IDS.keys())
    league_name = leagues[league_idx]

    try:
        valid_matches, invalid_matches = schedule_service.get_matches_with_valid_mapping(league_name)

        if not valid_matches:
            await update.callback_query.edit_message_text(
                f"❌ Нет доступных матчей для анализа в {league_name}.",
                parse_mode='HTML'
            )
            return

        text = f"🤖 <b>LLM анализ - {league_name}</b>\n\n"
        text += "Выберите матч для глубокого анализа:\n\n"

        keyboard = []
        for match in valid_matches:
            button_text = f"🏠 {match['home_team']} vs ✈️ {match['away_team']}"
            callback_data = f"llm_match_{match['home_team']}_{match['away_team']}"
            keyboard.append([InlineKeyboardButton(button_text, callback_data=callback_data)])

        keyboard.append([InlineKeyboardButton("🔙 Назад", callback_data="prediction_llm")])

        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.callback_query.edit_message_text(text, reply_markup=reply_markup, parse_mode='HTML')

    except Exception as e:
        logger.error(f"Ошибка получения матчей для LLM анализа: {e}")
        await update.callback_query.edit_message_text(
            f"❌ Ошибка при получении матчей {league_name}.",
            parse_mode='HTML'
        )


async def process_llm_analysis(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка LLM анализа матча"""
    query = update.callback_query
    data = query.data

    parts = data.split('_')
    home_team = parts[2]
    away_team = parts[3]

    mapped_home, mapped_away, success, error = team_mapper.validate_mapping(home_team, away_team)

    if not success:
        await query.edit_message_text(
            f"❌ <b>Ошибка преобразования названий команд</b>\n\n{error}",
            parse_mode='HTML'
        )
        return

    # Показываем загрузку
    loading_msg = await query.edit_message_text(
        f"🤖 <b>Глубокий анализ матча</b>\n\n"
        f"🏠 {mapped_home} vs ✈️ {mapped_away}\n\n"
        f"⏳ Собираю данные и анализирую...\n"
        f"<i>Это может занять 10-15 секунд</i>",
        parse_mode='HTML'
    )

    try:
        # Сначала получаем базовый прогноз
        if not init_coordinator():
            await query.edit_message_text("❌ Ошибка инициализации системы.")
            return

        # Получаем детальный прогноз для анализа
        result = coordinator.predict_match(mapped_home, mapped_away)

        if not result['success']:
            await query.edit_message_text(f"❌ Ошибка прогноза: {result.get('error')}")
            return

        # Получаем LLM анализ
        analysis = llm_analysis_service.create_match_analysis(
            mapped_home, mapped_away, result
        )

        # Создаем детальный прогноз для отображения
        detailed_report = format_detailed_prediction(result)

        # Извлекаем основную часть детального прогноза
        detailed_sections = detailed_report.split('━━━━━━━━━━━━━━━━━━━━━━━━')
        main_prediction = detailed_sections[1] if len(detailed_sections) > 1 else detailed_report

        # Форматируем финальный отчет
        report = f"""
            🤖 <b>ГЛУБОКИЙ АНАЛИЗ МАТЧА</b>
            
            🏠 {mapped_home} vs ✈️ {mapped_away}
            
            ━━━━━━━━━━━━━━━━━━━━━━━━
            🎯 <b>ОСНОВНОЙ ПРОГНОЗ</b>
            
            {main_prediction}
            
            ━━━━━━━━━━━━━━━━━━━━━━━━
            🧠 <b>AI АНАЛИЗ</b>
            
            {analysis}
            
            ━━━━━━━━━━━━━━━━━━━━━━━━
            💡 <i>Анализ создан с помощью DeepSeek R1 Chimera</i>
            """

        # Проверяем длину сообщения
        if len(report) > 4000:
            report = report[:4000] + "\n\n... (сообщение сокращено)"

        keyboard = [
            [InlineKeyboardButton("🔄 Новый анализ", callback_data="prediction_llm")],
            [InlineKeyboardButton("📊 Обычный прогноз", callback_data="prediction_detailed")],
            [InlineKeyboardButton("🏠 Главное меню", callback_data="main_menu")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await query.edit_message_text(report, reply_markup=reply_markup, parse_mode='HTML')

    except Exception as e:
        logger.error(f"Ошибка LLM анализа: {e}", exc_info=True)
        await query.edit_message_text(
            f"❌ <b>Ошибка анализа</b>\n\n"
            f"Не удалось выполнить глубокий анализ матча.\n"
            f"Попробуйте позже или используйте обычный прогноз.",
            parse_mode='HTML'
        )


def register_prediction_handlers(app):
    """Регистрирует обработчики прогнозов"""
    app.add_handler(CommandHandler('teams', list_teams))
    app.add_handler(CommandHandler('status', status))
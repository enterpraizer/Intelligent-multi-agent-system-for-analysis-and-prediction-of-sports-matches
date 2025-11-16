"""
Обработчики статистики команд
"""
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes, CallbackQueryHandler
from Foot_analisys.src.bot.services.team_stats_service import team_stats_service
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

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

async def show_team_stats_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Меню выбора команды для статистики"""
    keyboard = [
        [InlineKeyboardButton("🔍 Поиск команды", callback_data="stats_search")],
        [InlineKeyboardButton("⭐ Популярные команды", callback_data="stats_popular")],
        [InlineKeyboardButton("📋 Список всех команд", callback_data="stats_all")],
        [InlineKeyboardButton("🔙 Назад", callback_data="menu_stats")]
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.callback_query.edit_message_text(
        "📈 <b>Статистика команды</b>\n\n"
        "Выберите способ поиска команды:",
        reply_markup=reply_markup,
        parse_mode='HTML'
    )

async def show_popular_teams(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показать популярные команды"""
    popular_teams = team_stats_service.popular_teams

    keyboard = []
    teams_list = list(popular_teams.items())

    for i in range(0, len(teams_list), 2):
        row = []
        team1_name, team1_id = teams_list[i]
        row.append(InlineKeyboardButton(team1_name, callback_data=f"stats_team_{team1_id}"))

        if i + 1 < len(teams_list):
            team2_name, team2_id = teams_list[i + 1]
            row.append(InlineKeyboardButton(team2_name, callback_data=f"stats_team_{team2_id}"))

        keyboard.append(row)

    keyboard.append([InlineKeyboardButton("🔙 Назад", callback_data="stats_team")])

    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.callback_query.edit_message_text(
        "⭐ <b>Популярные команды</b>\n\n"
        "Выберите команду для просмотра статистики:",
        reply_markup=reply_markup,
        parse_mode='HTML'
    )

async def show_all_teams(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показать все команды по лигам"""
    leagues = team_stats_service.get_all_teams_by_league()

    # Создаем меню выбора лиги
    keyboard = []
    for league_name in ["EPL", "LL", "Bundes Ligue", "Serie A", "Ligue1", "Other"]:
        if leagues[league_name]:
            keyboard.append([InlineKeyboardButton(f"🏆 {league_name}", callback_data=f"stats_league_{league_name}")])

    keyboard.append([InlineKeyboardButton("🔙 Назад", callback_data="stats_team")])

    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.callback_query.edit_message_text(
        "📋 <b>Все команды по лигам</b>\n\n"
        "Выберите лигу для просмотра команд:",
        reply_markup=reply_markup,
        parse_mode='HTML'
    )

async def show_teams_by_league(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показать команды конкретной лиги"""
    league_name = update.callback_query.data.split('_')[2]
    leagues = team_stats_service.get_all_teams_by_league()
    teams = leagues.get(league_name, {})

    if not teams:
        await update.callback_query.edit_message_text(
            f"❌ <b>Нет команд в лиге {league_name}</b>",
            parse_mode='HTML'
        )
        return

    # Создаем пагинацию (по 15 команд на страницу)
    teams_list = list(teams.items())
    page = context.user_data.get('teams_page', 0)
    start_idx = page * 15
    end_idx = start_idx + 15

    current_teams = teams_list[start_idx:end_idx]

    keyboard = []
    for i in range(0, len(current_teams), 2):
        row = []
        team1_name, team1_id = current_teams[i]
        row.append(InlineKeyboardButton(team1_name, callback_data=f"stats_team_{team1_id}"))

        if i + 1 < len(current_teams):
            team2_name, team2_id = current_teams[i + 1]
            row.append(InlineKeyboardButton(team2_name, callback_data=f"stats_team_{team2_id}"))

        keyboard.append(row)

    # Кнопки навигации
    nav_buttons = []
    if page > 0:
        nav_buttons.append(InlineKeyboardButton("⬅️ Назад", callback_data=f"stats_league_{league_name}_page_{page-1}"))
    if end_idx < len(teams_list):
        nav_buttons.append(InlineKeyboardButton("Вперед ➡️", callback_data=f"stats_league_{league_name}_page_{page+1}"))

    if nav_buttons:
        keyboard.append(nav_buttons)

    keyboard.append([InlineKeyboardButton("🔙 Назад к лигам", callback_data="stats_all")])

    reply_markup = InlineKeyboardMarkup(keyboard)

    total_pages = (len(teams_list) + 14) // 15  # Округление вверх

    await update.callback_query.edit_message_text(
        f"🏆 <b>Команды {league_name}</b>\n\n"
        f"Страница {page + 1} из {total_pages}\n"
        f"Выберите команду для просмотра статистики:",
        reply_markup=reply_markup,
        parse_mode='HTML'
    )

    # Сохраняем текущую страницу
    context.user_data['teams_page'] = page

async def handle_league_page(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка переключения страниц в списке команд"""
    parts = update.callback_query.data.split('_')
    league_name = parts[2]
    page = int(parts[4])

    # Обновляем страницу в user_data
    context.user_data['teams_page'] = page

    # Показываем команды с новой страницей
    await show_teams_by_league(update, context)

async def start_team_search(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Начало поиска команды"""
    await update.callback_query.edit_message_text(
        "🔍 <b>Поиск команды</b>\n\n"
        "Введите название команды для поиска:\n\n"
        "<i>Примеры: Manchester United, Barcelona, Bayern Munich</i>",
        parse_mode='HTML'
    )

    # Устанавливаем состояние поиска
    context.user_data['waiting_for_team_search'] = True

async def handle_team_search(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка поиска команды"""
    if not context.user_data.get('waiting_for_team_search'):
        return

    query = update.message.text.strip()

    if len(query) < 3:
        await update.message.reply_text(
            "❌ <b>Слишком короткий запрос</b>\n\n"
            "Введите хотя бы 3 символа для поиска.",
            parse_mode='HTML'
        )
        return

    # Показываем загрузку
    search_msg = await update.message.reply_text(
        f"🔍 Ищу команды по запросу: <b>{query}</b>...",
        parse_mode='HTML'
    )

    # Ищем команды
    teams = team_stats_service.search_teams(query)

    if not teams:
        await search_msg.edit_text(
            f"❌ <b>Команды не найдены</b>\n\n"
            f"По запросу '<b>{query}</b>' ничего не найдено.\n"
            f"Попробуйте другой запрос.",
            parse_mode='HTML'
        )
        context.user_data['waiting_for_team_search'] = False
        return

    # Создаем клавиатуру с результатами
    keyboard = []
    for team in teams[:8]:  # Ограничиваем количество результатов
        button_text = f"🏴 {team['name']}"
        if team.get('league') and team['league'] != 'Other':
            button_text += f" ({team['league']})"
        callback_data = f"stats_team_{team['id']}"
        keyboard.append([InlineKeyboardButton(button_text, callback_data=callback_data)])

    keyboard.append([InlineKeyboardButton("🔙 Назад", callback_data="stats_team")])

    reply_markup = InlineKeyboardMarkup(keyboard)

    await search_msg.edit_text(
        f"🔍 <b>Результаты поиска</b>\n\n"
        f"Найдено команд по запросу '<b>{query}</b>':\n\n"
        f"Выберите команду для просмотра статистики:",
        reply_markup=reply_markup,
        parse_mode='HTML'
    )

    context.user_data['waiting_for_team_search'] = False


async def show_team_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показать статистику команды с кнопкой избранного"""
    query = update.callback_query
    team_id = int(query.data.split('_')[2])
    user_id = query.from_user.id

    # Показываем загрузку
    await query.edit_message_text(
        "📊 <b>Загрузка статистики...</b>\n\n"
        "⏳ Получаю данные о команде...",
        parse_mode='HTML'
    )

    try:
        # Получаем статистику
        stats = team_stats_service.get_team_stats(team_id)

        if not stats:
            await query.edit_message_text(
                "❌ <b>Ошибка загрузки статистики</b>\n\n"
                "Не удалось получить данные о команде.\n"
                "Попробуйте позже.",
                parse_mode='HTML'
            )
            return

        team_info = stats['team_info']
        standing = stats['standing']
        form_stats = stats['form']
        series = stats['series']
        home_away = stats['home_away']
        matches = stats['matches']

        # Форматируем отчет с добавлением матчей
        report = format_team_stats_report(
            team_info, standing, form_stats, series, home_away, matches
        )

        # Определяем текст кнопки избранного
        from Foot_analisys.src.bot.utils.user_data import is_team_favorite
        if is_team_favorite(user_id, team_id):
            favorite_button_text = "❌ Удалить из избранного"
        else:
            favorite_button_text = "⭐ Добавить в избранное"

        # Кнопки навигации
        keyboard = [
            [InlineKeyboardButton(favorite_button_text, callback_data=f"favorite_toggle_{team_id}")],
            [InlineKeyboardButton("🔄 Обновить", callback_data=f"stats_team_{team_id}")],
            [InlineKeyboardButton("📈 Новая статистика", callback_data="stats_team")],
            [InlineKeyboardButton("🏠 Главное меню", callback_data="main_menu")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await query.edit_message_text(report, reply_markup=reply_markup, parse_mode='HTML')

    except Exception as e:
        logger.error(f"Ошибка показа статистики команды: {e}")
        await query.edit_message_text(
            "❌ <b>Ошибка загрузки статистики</b>\n\n"
            "Произошла ошибка при получении данных.\n"
            "Попробуйте позже.",
            parse_mode='HTML'
        )


def format_team_stats_report(team_info, standing, form_stats, series, home_away, matches):
    """Форматирует отчет о статистике команды с последними матчами"""
    team_name = team_info['name']
    venue = team_info.get('venue', 'Неизвестно')
    founded = team_info.get('founded', 'Неизвестно')
    colors = team_info.get('clubColors', 'Неизвестно')

    report = f"📊 <b>Статистика команды: {team_name}</b>\n\n"

    # Основная информация
    report += "🏟️ <b>Основная информация</b>\n"
    report += f"• Стадион: {venue}\n"
    if founded != 'Неизвестно':
        report += f"• Основана: {founded}\n"
    report += f"• Цвета: {colors}\n\n"

    # Позиция в таблице
    if standing:
        report += "📈 <b>Позиция в таблице</b>\n"
        report += f"• Место: {standing['position']}\n"
        report += f"• Очки: {standing['points']}\n"
        report += f"• Матчи: {standing['playedGames']}\n"
        report += f"• Победы/Ничьи/Поражения: {standing['won']}/{standing['draw']}/{standing['lost']}\n"
        report += f"• Забито/Пропущено: {standing['goalsFor']}/{standing['goalsAgainst']}\n\n"
    else:
        report += "📈 <b>Позиция в таблице</b>\n"
        report += "• Данные о позиции недоступны\n\n"

    # Форма
    report += "📅 <b>Форма (последние 5 матчей)</b>\n"
    if form_stats['form']:
        report += f"• Форма: {form_stats['form']} \n"
        report += f"• Очки: {form_stats['points']}\n"
        report += f"• Победы/Ничьи/Поражения: {form_stats['wins']}/{form_stats['draws']}/{form_stats['losses']}\n"
        report += f"• Средние голы: {form_stats['goals_for_avg']:.1f} забито, {form_stats['goals_against_avg']:.1f} пропущено\n"
        report += f"• Сухие матчи: {form_stats['clean_sheets']}\n\n"
    else:
        report += "• Данные о форме недоступны\n\n"

    # Серии
    report += "🔥 <b>Текущие серии</b>\n"
    if series['unbeaten'] > 0 or series['win_streak'] > 0:
        report += f"• Без поражений: {series['unbeaten']} матчей\n"
        report += f"• Победная серия: {series['win_streak']} матчей\n\n"
    else:
        report += "• Данные о сериях недоступны\n\n"

    # Статистика дома/в гостях
    report += "🏠✈️ <b>Статистика дома/в гостях (последние 5 матчей)</b>\n"

    home_matches = home_away['home']['W'] + home_away['home']['D'] + home_away['home']['L']
    away_matches = home_away['away']['W'] + home_away['away']['D'] + home_away['away']['L']

    if home_matches > 0:
        report += f"\n🏠 Дома:\n"
        report += f"• Матчи: {home_matches}\n"
        report += f"• Победы/Ничьи/Поражения: {home_away['home']['W']}/{home_away['home']['D']}/{home_away['home']['L']}\n"
        report += f"• Голы: {home_away['home']['GF']} забито, {home_away['home']['GA']} пропущено\n"
        report += f"• Средние: {home_away['home']['GF_avg']:.1f} забито, {home_away['home']['GA_avg']:.1f} пропущено\n"
        report += f"• Сухие матчи: {home_away['home']['CS']}\n"

    if away_matches > 0:
        report += f"\n✈️ В гостях:\n"
        report += f"• Матчи: {away_matches}\n"
        report += f"• Победы/Ничьи/Поражения: {home_away['away']['W']}/{home_away['away']['D']}/{home_away['away']['L']}\n"
        report += f"• Голы: {home_away['away']['GF']} забито, {home_away['away']['GA']} пропущено\n"
        report += f"• Средние: {home_away['away']['GF_avg']:.1f} забито, {home_away['away']['GA_avg']:.1f} пропущено\n"
        report += f"• Сухие матчи: {home_away['away']['CS']}\n"

    if home_matches == 0 and away_matches == 0:
        report += "\n• Данные о домашних и гостевых матчах недоступны\n"

    # Последние 5 матчей
    report += "\n⚽ <b>Последние 5 матчей</b>\n"
    if matches and len(matches) >= 5:
        last_5_matches = matches[-5:]
        for m in reversed(last_5_matches):  # Показываем от самых свежих к старым
            dt = datetime.fromisoformat(m["utcDate"].replace("Z", "+00:00"))
            home_team = m["homeTeam"]["name"]
            away_team = m["awayTeam"]["name"]
            score = m["score"]["fullTime"]

            # Определяем эмодзи для результата
            is_home = m["homeTeam"]["id"] == team_info['id']
            gf = score["home"] if is_home else score["away"]
            ga = score["away"] if is_home else score["home"]

            if gf > ga:
                result_emoji = "✅"
            elif gf == ga:
                result_emoji = "⚪"
            else:
                result_emoji = "❌"

            report += f"\n{result_emoji} {dt:%d.%m.%Y}\n"
            report += f"   🏠 {home_team} {score['home']}:{score['away']} {away_team} ✈️\n"
    else:
        report += "\n• Данные о последних матчах недоступны\n"

    return report

def register_stats_handlers(app):
    """Регистрирует обработчики статистики"""
    # Обработчики регистрируются через CallbackQueryHandler в главном файле
    pass
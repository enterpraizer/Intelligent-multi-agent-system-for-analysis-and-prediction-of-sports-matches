"""
Обработчики расписания матчей
"""
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes
from Foot_analisys.src.bot.services.schedule_service import schedule_service
import logging

logger = logging.getLogger(__name__)

async def show_schedule_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Меню расписания матчей"""
    keyboard = [
        [InlineKeyboardButton("📅 Ближайшие матчи", callback_data="schedule_upcoming")],
        [InlineKeyboardButton("🏆 По лигам", callback_data="schedule_leagues")],
        [InlineKeyboardButton("🔍 Поиск матча", callback_data="schedule_search")],
        [InlineKeyboardButton("🔙 Назад", callback_data="main_menu")]
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.callback_query.edit_message_text(
        "📅 <b>Расписание матчей</b>\n\n"
        "Выберите способ поиска:",
        reply_markup=reply_markup,
        parse_mode='HTML'
    )

async def show_upcoming_matches(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показать ближайшие матчи всех лиг"""
    try:
        matches = schedule_service.get_all_upcoming_matches(limit_per_league=3)

        if not matches:
            await update.callback_query.edit_message_text(
                "❌ Не удалось получить расписание матчей.\n"
                "Попробуйте позже.",
                parse_mode='HTML'
            )
            return

        text = "📅 <b>Ближайшие матчи</b>\n\n"

        current_league = None
        match_count = 0

        for match in matches:
            formatted = schedule_service.format_match_for_display(match)

            if formatted['league'] != current_league:
                current_league = formatted['league']
                text += f"\n🏆 <b>{current_league}</b>\n"

            # Показываем оригинальные названия, но отмечаем если есть маппинг
            home_display = formatted['home_team']
            away_display = formatted['away_team']

            if formatted['mapping_success']:
                text += f"• {formatted['date']}\n"
                text += f"  🏠 {home_display} vs ✈️ {away_display}\n"
                text += f"  ✅ Доступен прогноз\n\n"
            else:
                text += f"• {formatted['date']}\n"
                text += f"  🏠 {home_display} vs ✈️ {away_display}\n"
                text += f"  ❌ Прогноз недоступен\n\n"

            match_count += 1
            if match_count >= 15:
                text += "\n... и другие матчи"
                break

        keyboard = [
            [InlineKeyboardButton("🎯 Сделать прогноз", callback_data="menu_prediction")],
            [InlineKeyboardButton("🔙 Назад", callback_data="menu_schedule")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await update.callback_query.edit_message_text(text, reply_markup=reply_markup, parse_mode='HTML')

    except Exception as e:
        logger.error(f"Ошибка получения расписания: {e}")
        await update.callback_query.edit_message_text(
            "❌ Ошибка при получении расписания.",
            parse_mode='HTML'
        )

async def show_schedule_leagues(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Выбор лиги для просмотра расписания"""
    keyboard = []
    leagues = list(schedule_service.LEAGUE_IDS.keys())

    for i in range(0, len(leagues), 2):
        row = []
        row.append(InlineKeyboardButton(leagues[i], callback_data=f"schedule_league_{i}"))
        if i + 1 < len(leagues):
            row.append(InlineKeyboardButton(leagues[i + 1], callback_data=f"schedule_league_{i + 1}"))
        keyboard.append(row)

    keyboard.append([InlineKeyboardButton("🔙 Назад", callback_data="menu_schedule")])

    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.callback_query.edit_message_text(
        "🏆 <b>Расписание по лигам</b>\n\n"
        "Выберите лигу:",
        reply_markup=reply_markup,
        parse_mode='HTML'
    )

async def show_league_schedule(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показать расписание конкретной лиги"""
    league_idx = int(update.callback_query.data.split('_')[2])
    leagues = list(schedule_service.LEAGUE_IDS.keys())
    league_name = leagues[league_idx]

    try:
        matches = schedule_service.get_matches_by_league(league_name)

        if not matches:
            await update.callback_query.edit_message_text(
                f"❌ Нет данных о предстоящих матчах в {league_name}.",
                parse_mode='HTML'
            )
            return

        text = f"📅 <b>Расписание - {league_name}</b>\n\n"

        for match in matches:
            status_icon = "✅" if match['mapping_success'] else "❌"
            text += f"• {match['date']} {status_icon}\n"
            text += f"  🏠 {match['home_team']} vs ✈️ {match['away_team']}\n\n"

        keyboard = [
            [InlineKeyboardButton("🎯 Сделать прогноз", callback_data="menu_prediction")],
            [InlineKeyboardButton("🔙 Назад", callback_data="schedule_leagues")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await update.callback_query.edit_message_text(text, reply_markup=reply_markup, parse_mode='HTML')

    except Exception as e:
        logger.error(f"Ошибка получения расписания лиги: {e}")
        await update.callback_query.edit_message_text(
            f"❌ Ошибка при получении расписания {league_name}.",
            parse_mode='HTML'
        )

def register_schedule_handlers(app):
    """Регистрирует обработчики расписания"""
    pass
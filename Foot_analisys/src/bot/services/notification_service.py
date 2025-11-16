# services/notification_service.py
import asyncio
from datetime import datetime, timedelta
import logging
from Foot_analisys.src.bot.services.schedule_service import schedule_service
from Foot_analisys.src.bot.utils.user_data import get_user_data, user_data_store

logger = logging.getLogger(__name__)


class NotificationService:
    def __init__(self, application):
        self.app = application
        self.is_running = False

    async def start_scheduler(self):
        """Запуск планировщика уведомлений"""
        self.is_running = True
        while self.is_running:
            try:
                await self.check_upcoming_matches()
                await asyncio.sleep(300)  # Проверка каждые 5 минут
            except Exception as e:
                logger.error(f"Ошибка в планировщике: {e}")
                await asyncio.sleep(60)

    async def check_upcoming_matches(self):
        """Проверка предстоящих матчей для уведомлений"""
        try:
            # Получаем все матчи на ближайшие 2 дня
            all_matches = schedule_service.get_all_upcoming_matches(limit_per_league=20)

            for user_id, user_data in user_data_store.items():
                if not user_data['notifications']['enabled']:
                    continue

                await self.check_user_notifications(user_id, user_data, all_matches)

        except Exception as e:
            logger.error(f"Ошибка проверки матчей: {e}")

    async def check_user_notifications(self, user_id, user_data, all_matches):
        """Проверка уведомлений для конкретного пользователя"""
        favorite_team_ids = [team['id'] for team in user_data['favorite_teams']]
        notification_time = user_data['notifications']['time_before_match']

        for match in all_matches:
            match_time = datetime.fromisoformat(match["utcDate"].replace("Z", "+00:00"))
            time_until_match = match_time - datetime.now()

            # Проверяем, подходит ли время для уведомления
            if timedelta(hours=notification_time - 1) < time_until_match <= timedelta(hours=notification_time):

                # Проверяем, участвует ли избранная команда
                home_team_id = match["homeTeam"].get("id")
                away_team_id = match["awayTeam"].get("id")

                if home_team_id in favorite_team_ids or away_team_id in favorite_team_ids:
                    await self.send_match_notification(user_id, match, notification_time)

    async def send_match_notification(self, user_id, match, hours_before):
        """Отправка уведомления о матче"""
        try:
            home_team = match["homeTeam"]["name"]
            away_team = match["awayTeam"]["name"]
            match_time = datetime.fromisoformat(match["utcDate"].replace("Z", "+00:00"))
            league = match.get('league_name', 'Неизвестная лига')

            # Форматируем время
            match_time_str = match_time.strftime("%d.%m.%Y в %H:%M")

            message = (
                f"🔔 <b>Напоминание о матче</b>\n\n"
                f"🏆 <b>{league}</b>\n"
                f"⚽ <b>{home_team} vs {away_team}</b>\n"
                f"🕐 Матч начнется: {match_time_str}\n"
                f"⏰ Через {hours_before} часов\n\n"
                f"🎯 <a href='tg://resolve?domain=your_bot&start=prediction'>Сделать прогноз</a>"
            )

            await self.app.bot.send_message(
                chat_id=user_id,
                text=message,
                parse_mode='HTML',
                disable_web_page_preview=True
            )

            logger.info(f"Отправлено уведомление пользователю {user_id} о матче {home_team} vs {away_team}")

        except Exception as e:
            logger.error(f"Ошибка отправки уведомления: {e}")

    def stop_scheduler(self):
        """Остановка планировщика"""
        self.is_running = False


# Глобальный экземпляр
notification_service = None
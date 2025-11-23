"""
Сервис для получения расписания матчей через football-data.org API
"""
import requests
from datetime import datetime
import logging
from Foot_analisys.src.bot.services.team_mapper import team_mapper

logger = logging.getLogger(__name__)

class ScheduleService:
    def __init__(self):
        self.API_TOKEN = "8b9004850ee441d7be14912d5a97a698"
        self.BASE_URL = "https://api.football-data.org/v4"

        self.headers = {
            "X-Auth-Token": self.API_TOKEN
        }

        # Соответствие названий лиг их ID в football-data.org
        self.LEAGUE_IDS = {
            "EPL": "PL",           # Premier League
            "LL": "PD",            # La Liga
            "Bundes Ligue": "BL1", # Bundesliga
            "Serie A": "SA",       # Serie A
            "Ligue1": "FL1"        # Ligue 1
        }

        # Маппинг для обратного соответствия
        self.LEAGUE_NAMES = {v: k for k, v in self.LEAGUE_IDS.items()}

    def get_upcoming_matches(self, league_code, limit=10):
        """Получить ближайшие матчи лиги"""
        try:
            url = f"{self.BASE_URL}/competitions/{league_code}/matches"
            params = {"status": "SCHEDULED"}
            response = requests.get(url, headers=self.headers, params=params)

            if response.status_code != 200:
                logger.error(f"API Error: {response.status_code} - {response.text}")
                return []

            data = response.json()
            matches = data.get("matches", [])

            # Сортируем по дате и ограничиваем количество
            matches = sorted(matches, key=lambda m: m["utcDate"])
            return matches[:limit]

        except Exception as e:
            logger.error(f"Ошибка получения расписания: {e}")
            return []

    def get_all_upcoming_matches(self, limit_per_league=5):
        """Получить матчи всех лиг"""
        all_matches = []

        for league_name, code in self.LEAGUE_IDS.items():
            matches = self.get_upcoming_matches(code, limit_per_league)
            for match in matches:
                match['league_name'] = league_name
                match['league_code'] = code
                all_matches.append(match)

        # Сортируем все матчи по дате
        return sorted(all_matches, key=lambda m: m["utcDate"])

    def format_match_for_display(self, match):
        """Форматировать матч для отображения"""
        home_team = match["homeTeam"]["name"]
        away_team = match["awayTeam"]["name"]
        date = datetime.fromisoformat(match["utcDate"].replace("Z", "+00:00"))

        from datetime import timedelta
        date = date + timedelta(hours=3)

        # Пробуем преобразовать названия команд
        mapped_home, mapped_away, success, error = team_mapper.validate_mapping(home_team, away_team)

        return {
            'home_team': home_team,
            'away_team': away_team,
            'mapped_home_team': mapped_home,
            'mapped_away_team': mapped_away,
            'mapping_success': success,
            'mapping_error': error,
            'date': date.strftime("%Y-%m-%d %H:%M"),
            'datetime': date,
            'league': match.get('league_name', 'Unknown'),
            'match_id': match.get('id')
        }

    def get_matches_by_league(self, league_name):
        """Получить матчи конкретной лиги"""
        league_code = self.LEAGUE_IDS.get(league_name)
        if not league_code:
            return []

        matches = self.get_upcoming_matches(league_code, limit=10)
        return [self.format_match_for_display(match) for match in matches]

    def find_team_matches(self, team_name, limit=5):
        """Найти матчи команды"""
        all_matches = self.get_all_upcoming_matches(limit_per_league=10)
        team_matches = []

        for match in all_matches:
            home_team = match["homeTeam"]["name"].lower()
            away_team = match["awayTeam"]["name"].lower()
            search_name = team_name.lower()

            if search_name in home_team or search_name in away_team:
                team_matches.append(self.format_match_for_display(match))

            if len(team_matches) >= limit:
                break

        return team_matches

    def get_matches_with_valid_mapping(self, league_name):
        """
        Получить матчи лиги только с успешным маппингом названий

        Returns:
            list: Матчи с успешным маппингом
            list: Матчи с ошибками маппинга (для отладки)
        """
        matches = self.get_matches_by_league(league_name)
        valid_matches = []
        invalid_matches = []

        for match in matches:
            if match['mapping_success']:
                valid_matches.append(match)
            else:
                invalid_matches.append(match)

        return valid_matches, invalid_matches

# Глобальный экземпляр сервиса
schedule_service = ScheduleService()
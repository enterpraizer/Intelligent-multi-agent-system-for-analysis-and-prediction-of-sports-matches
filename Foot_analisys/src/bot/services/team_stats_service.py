"""
Сервис для получения статистики команд через football-data.org API
"""
import requests
from datetime import datetime
import logging
from Foot_analisys.src.bot.services.team_mapper import team_mapper

logger = logging.getLogger(__name__)

class TeamStatsService:
    def __init__(self):
        self.API_TOKEN = "8b9004850ee441d7be14912d5a97a698"
        self.BASE_URL = "https://api.football-data.org/v4"
        self.headers = {"X-Auth-Token": self.API_TOKEN}

        # ПОЛНАЯ БАЗА ID ДЛЯ ВСЕХ 164 КОМАНД ИЗ ДАТАСЕТА
        self.all_teams = {
            # Английская Премьер-лига
            "Arsenal": 57,
            "Aston Villa": 58,
            "Bournemouth": 1044,
            "Brentford": 402,
            "Brighton": 397,
            "Burnley": 328,
            "Chelsea": 61,
            "Crystal Palace": 354,
            "Everton": 62,
            "Fulham": 63,
            "Liverpool": 64,
            "Luton": 389,
            "Man City": 65,
            "Man United": 66,
            "Newcastle": 67,
            "Nott'm Forest": 351,
            "Sheffield United": 356,
            "Tottenham": 73,
            "West Ham": 563,
            "Wolves": 76,

            # Ла Лига
            "Alaves": 263,
            "Almeria": 267,
            "Ath Bilbao": 77,
            "Ath Madrid": 78,
            "Barcelona": 81,
            "Betis": 90,
            "Cadiz": 264,
            "Celta": 558,
            "Eibar": 278,
            "Elche": 285,
            "Espanol": 80,
            "Getafe": 82,
            "Girona": 298,
            "Granada": 83,
            "Las Palmas": 275,
            "Leganes": 745,
            "Levante": 88,
            "Mallorca": 89,
            "Osasuna": 79,
            "Real Madrid": 86,
            "Sevilla": 559,
            "Sociedad": 92,
            "Valencia": 95,
            "Vallecano": 87,
            "Villarreal": 94,

            # Бундеслига
            "Augsburg": 170,
            "Bayer Leverkusen": 6,
            "Bayern Munich": 5,
            "Bochum": 36,
            "Bremen": 12,
            "Darmstadt": 181,
            "Dortmund": 4,
            "Ein Frankfurt": 19,
            "FC Koln": 1,
            "Freiburg": 17,
            "Heidenheim": 44,
            "Hertha": 9,
            "Hoffenheim": 2,
            "Mainz": 15,
            "M'gladbach": 18,
            "RB Leipzig": 721,
            "Stuttgart": 10,
            "Union Berlin": 28,
            "Wolfsburg": 11,

            # Серия А
            "Atalanta": 102,
            "Bologna": 103,
            "Cagliari": 104,
            "Empoli": 445,
            "Fiorentina": 99,
            "Frosinone": 487,
            "Genoa": 107,
            "Inter": 108,
            "Juventus": 109,
            "Lazio": 110,
            "Lecce": 866,
            "Milan": 98,
            "Monza": 1577,
            "Napoli": 113,
            "Roma": 100,
            "Salernitana": 379,
            "Sassuolo": 471,
            "Torino": 586,
            "Udinese": 115,
            "Verona": 450,

            # Лига 1
            "Clermont": 99,
            "Le Havre": 111,
            "Lens": 116,
            "Lille": 79,
            "Lorient": 97,
            "Lyon": 104,
            "Marseille": 81,
            "Metz": 112,
            "Monaco": 91,
            "Montpellier": 82,
            "Nantes": 83,
            "Nice": 84,
            "Paris SG": 524,
            "Reims": 93,
            "Rennes": 94,
            "Strasbourg": 95,
            "Toulouse": 96,

            # Другие команды (исторические/вторые дивизионы)
            "Ajaccio": 510,
            "Ajaccio GFCO": 595,
            "Amiens": 530,
            "Angers": 77,
            "Auxerre": 519,
            "Bastia": 518,
            "Benevento": 1103,
            "Bielefeld": 23,
            "Bordeaux": 526,
            "Brescia": 455,
            "Brest": 106,
            "Caen": 514,
            "Cardiff": 715,
            "Carpi": 445,
            "Cesena": 455,
            "Chievo": 106,
            "Como": 470,
            "Cordoba": 278,
            "Cremonese": 472,
            "Crotone": 472,
            "Dijon": 526,
            "Evian Thonon Gaillard": 529,
            "Fortuna Dusseldorf": 185,
            "Greuther Furth": 176,
            "Guingamp": 538,
            "Hamburg": 7,
            "Hannover": 8,
            "Holstein Kiel": 182,
            "Huddersfield": 394,
            "Huesca": 299,
            "Hull": 322,
            "Ingolstadt": 174,
            "Ipswich": 57,
            "La Coruna": 560,
            "Leeds": 341,
            "Leicester": 338,
            "Malaga": 84,
            "Middlesbrough": 343,
            "Nancy": 521,
            "Nimes": 522,
            "Norwich": 68,
            "Nurnberg": 14,
            "Paderborn": 31,
            "Palermo": 449,
            "Parma": 112,
            "Pescara": 484,
            "QPR": 69,
            "Schalke 04": 6,
            "Sp Gijon": 560,
            "Spal": 455,
            "Spezia": 488,
            "St Etienne": 527,
            "St Pauli": 180,
            "Stoke": 70,
            "Sunderland": 71,
            "Swansea": 72,
            "Troyes": 531,
            "Venezia": 450,
            "Watford": 346,
            "West Brom": 74
        }

        # ID популярных команд для быстрого доступа
        self.popular_teams = {
            "Man United": 66,
            "Man City": 65,
            "Liverpool": 64,
            "Chelsea": 61,
            "Arsenal": 57,
            "Tottenham": 73,
            "Barcelona": 81,
            "Real Madrid": 86,
            "Ath Madrid": 78,
            "Bayern Munich": 5,
            "Dortmund": 4,
            "Juventus": 109,
            "Milan": 98,
            "Inter": 108,
            "PSG": 524
        }

        # Соответствие лиг
        self.LEAGUE_CODES = {
            "EPL": "PL",
            "LL": "PD",
            "Bundes Ligue": "BL1",
            "Serie A": "SA",
            "Ligue1": "FL1"
        }

    def search_teams(self, query: str):
        """Поиск команд по названию"""
        try:
            # Сначала ищем в локальной базе
            local_results = []
            query_lower = query.lower()

            for team_name, team_id in self.all_teams.items():
                if query_lower in team_name.lower():
                    local_results.append({
                        'id': team_id,
                        'name': team_name,
                        'short_name': team_name,
                        'crest': '',
                        'league': self._get_team_league_by_name(team_name)
                    })

            # Если есть локальные результаты, возвращаем их
            if local_results:
                return local_results[:8]

            # Если нет локальных результатов, ищем через API
            url = f"{self.BASE_URL}/teams"
            params = {"name": query}
            response = requests.get(url, headers=self.headers, params=params)

            if response.status_code != 200:
                logger.error(f"API Error: {response.status_code}")
                return []

            data = response.json()
            teams = data.get("teams", [])

            # Фильтруем и форматируем результаты
            formatted_teams = []
            for team in teams:
                formatted_teams.append({
                    'id': team['id'],
                    'name': team['name'],
                    'short_name': team.get('shortName', team['name']),
                    'crest': team.get('crest', ''),
                    'league': self._get_team_league(team)
                })

            return formatted_teams[:8]  # Ограничиваем количество результатов

        except Exception as e:
            logger.error(f"Ошибка поиска команд: {e}")
            return []

    def _get_team_league_by_name(self, team_name: str):
        """Определяет лигу команды по названию"""
        # Простая логика определения лиги по названию команды
        epl_teams = ["Arsenal", "Aston Villa", "Bournemouth", "Brentford", "Brighton",
                     "Burnley", "Chelsea", "Crystal Palace", "Everton", "Fulham",
                     "Liverpool", "Luton", "Man City", "Man United", "Newcastle",
                     "Nott'm Forest", "Sheffield United", "Tottenham", "West Ham", "Wolves"]

        laliga_teams = ["Alaves", "Almeria", "Ath Bilbao", "Ath Madrid", "Barcelona",
                       "Betis", "Cadiz", "Celta", "Eibar", "Elche", "Espanol",
                       "Getafe", "Girona", "Granada", "Las Palmas", "Leganes",
                       "Levante", "Mallorca", "Osasuna", "Real Madrid", "Sevilla",
                       "Sociedad", "Valencia", "Vallecano", "Villarreal"]

        bundesliga_teams = ["Augsburg", "Bayer Leverkusen", "Bayern Munich", "Bochum",
                           "Bremen", "Darmstadt", "Dortmund", "Ein Frankfurt", "FC Koln",
                           "Freiburg", "Heidenheim", "Hertha", "Hoffenheim", "Mainz",
                           "M'gladbach", "RB Leipzig", "Stuttgart", "Union Berlin", "Wolfsburg"]

        serie_a_teams = ["Atalanta", "Bologna", "Cagliari", "Empoli", "Fiorentina",
                        "Frosinone", "Genoa", "Inter", "Juventus", "Lazio", "Lecce",
                        "Milan", "Monza", "Napoli", "Roma", "Salernitana", "Sassuolo",
                        "Torino", "Udinese", "Verona"]

        ligue1_teams = ["Clermont", "Le Havre", "Lens", "Lille", "Lorient", "Lyon",
                       "Marseille", "Metz", "Monaco", "Montpellier", "Nantes", "Nice",
                       "Paris SG", "Reims", "Rennes", "Strasbourg", "Toulouse"]

        if team_name in epl_teams:
            return "EPL"
        elif team_name in laliga_teams:
            return "LL"
        elif team_name in bundesliga_teams:
            return "Bundes Ligue"
        elif team_name in serie_a_teams:
            return "Serie A"
        elif team_name in ligue1_teams:
            return "Ligue1"
        else:
            return "Other"

    def _get_team_league(self, team):
        """Определяет лигу команды через API"""
        competitions = team.get('runningCompetitions', [])
        for comp in competitions:
            code = comp.get('code', '')
            if code == 'PL':
                return "EPL"
            elif code == 'PD':
                return "LL"
            elif code == 'BL1':
                return "Bundes Ligue"
            elif code == 'SA':
                return "Serie A"
            elif code == 'FL1':
                return "Ligue1"
        return "Other"

    def get_all_teams_by_league(self):
        """Возвращает все команды сгруппированные по лигам"""
        leagues = {
            "EPL": {},
            "LL": {},
            "Bundes Ligue": {},
            "Serie A": {},
            "Ligue1": {},
            "Other": {}
        }

        for team_name, team_id in self.all_teams.items():
            league = self._get_team_league_by_name(team_name)
            leagues[league][team_name] = team_id

        return leagues

    def get_team_info(self, team_id):
        """Получает информацию о команде"""
        url = f"{self.BASE_URL}/teams/{team_id}"
        return requests.get(url, headers=self.headers).json()

    def get_team_matches(self, team_id, status="FINISHED", limit=10):
        """Получает матчи команды"""
        url = f"{self.BASE_URL}/teams/{team_id}/matches"
        params = {"status": status, "limit": limit}
        matches = requests.get(url, headers=self.headers, params=params).json().get("matches", [])
        matches.sort(key=lambda m: m["utcDate"])
        return matches

    def get_team_standing(self, team_id, competition_code):
        """Получает позицию в таблице"""
        url = f"{self.BASE_URL}/competitions/{competition_code}/standings"
        data = requests.get(url, headers=self.headers).json()
        for table in data.get("standings", []):
            for row in table.get("table", []):
                if row["team"]["id"] == team_id:
                    return row
        return None

    def calc_form(self, matches, team_id):
        """Рассчитывает форму команды"""
        last_matches = matches[-5:] if len(matches) >= 5 else matches
        stats = {
            "form": "",
            "points": 0,
            "wins": 0,
            "draws": 0,
            "losses": 0,
            "goals_for": 0,
            "goals_against": 0,
            "clean_sheets": 0
        }

        for m in last_matches:
            score = m["score"]["fullTime"]
            is_home = m["homeTeam"]["id"] == team_id
            gf = score["home"] if is_home else score["away"]
            ga = score["away"] if is_home else score["home"]

            stats["goals_for"] += gf
            stats["goals_against"] += ga

            if ga == 0:
                stats["clean_sheets"] += 1

            if gf > ga:
                stats["form"] += "W"
                stats["points"] += 3
                stats["wins"] += 1
            elif gf == ga:
                stats["form"] += "D"
                stats["points"] += 1
                stats["draws"] += 1
            else:
                stats["form"] += "L"
                stats["losses"] += 1

        n = len(last_matches)
        if n > 0:
            stats["goals_for_avg"] = stats["goals_for"] / n
            stats["goals_against_avg"] = stats["goals_against"] / n
        else:
            stats["goals_for_avg"] = 0
            stats["goals_against_avg"] = 0

        return stats

    def calc_series(self, matches, team_id):
        """Рассчитывает серии команды"""
        unbeaten = 0
        win_streak = 0

        for m in reversed(matches):
            score = m["score"]["fullTime"]
            is_home = m["homeTeam"]["id"] == team_id
            gf = score["home"] if is_home else score["away"]
            ga = score["away"] if is_home else score["home"]

            if gf >= ga:
                unbeaten += 1
            else:
                break

        for m in reversed(matches):
            score = m["score"]["fullTime"]
            is_home = m["homeTeam"]["id"] == team_id
            gf = score["home"] if is_home else score["away"]
            ga = score["away"] if is_home else score["home"]

            if gf > ga:
                win_streak += 1
            else:
                break

        return {"unbeaten": unbeaten, "win_streak": win_streak}

    def calc_home_away_stats(self, matches, team_id):
        """Статистика дома/в гостях"""
        last_matches = matches[-10:]  # Берем больше матчей для статистики
        stats = {
            "home": {"W":0, "D":0, "L":0, "GF":0, "GA":0, "CS":0},
            "away": {"W":0, "D":0, "L":0, "GF":0, "GA":0, "CS":0}
        }

        for m in last_matches:
            is_home = m["homeTeam"]["id"] == team_id
            side = "home" if is_home else "away"
            score = m["score"]["fullTime"]
            gf = score["home"] if is_home else score["away"]
            ga = score["away"] if is_home else score["home"]

            stats[side]["GF"] += gf
            stats[side]["GA"] += ga

            if ga == 0:
                stats[side]["CS"] += 1

            if gf > ga:
                stats[side]["W"] += 1
            elif gf == ga:
                stats[side]["D"] += 1
            else:
                stats[side]["L"] += 1

        for side in ["home", "away"]:
            n = sum(stats[side][k] for k in ["W", "D", "L"])
            stats[side]["GF_avg"] = stats[side]["GF"] / n if n else 0
            stats[side]["GA_avg"] = stats[side]["GA"] / n if n else 0

        return stats

    def get_team_stats(self, team_id, competition_code=None):
        """Получает полную статистику команды"""
        try:
            team = self.get_team_info(team_id)
            matches = self.get_team_matches(team_id)

            # Если лига не указана, пытаемся определить
            if not competition_code:
                competition_code = self._get_team_league(team)
                competition_code = self.LEAGUE_CODES.get(competition_code, "PL")

            stats = {
                'team_info': team,
                'matches': matches,  # Убедитесь что матчи включены
                'standing': self.get_team_standing(team_id, competition_code),
                'form': self.calc_form(matches, team_id),
                'series': self.calc_series(matches, team_id),
                'home_away': self.calc_home_away_stats(matches, team_id)
            }

            return stats

        except Exception as e:
            logger.error(f"Ошибка получения статистики команды {team_id}: {e}")
            return None

# Глобальный экземпляр сервиса
team_stats_service = TeamStatsService()
import logging
import re

logger = logging.getLogger(__name__)

class SimpleTeamMapper:
    def __init__(self):
        self.dataset_teams = [
            "Ajaccio", "Ajaccio GFCO", "Alaves", "Almeria", "Amiens", "Angers", "Arsenal", "Aston Villa",
            "Atalanta", "Ath Bilbao", "Ath Madrid", "Augsburg", "Auxerre", "Barcelona", "Bastia",
            "Bayern Munich", "Benevento", "Betis", "Bielefeld", "Bochum", "Bologna", "Bordeaux",
            "Bournemouth", "Brentford", "Brescia", "Brest", "Brighton", "Burnley", "Cadiz", "Caen",
            "Cagliari", "Cardiff", "Carpi", "Celta", "Cesena", "Chelsea", "Chievo", "Clermont",
            "Como", "Cordoba", "Cremonese", "Crotone", "Crystal Palace", "Darmstadt", "Dijon",
            "Dortmund", "Eibar", "Ein Frankfurt", "Elche", "Empoli", "Espanol", "Everton",
            "Evian Thonon Gaillard", "FC Koln", "Fiorentina", "Fortuna Dusseldorf", "Freiburg",
            "Frosinone", "Fulham", "Genoa", "Getafe", "Girona", "Granada", "Greuther Furth",
            "Guingamp", "Hamburg", "Hannover", "Heidenheim", "Hertha", "Hoffenheim", "Holstein Kiel",
            "Huddersfield", "Huesca", "Hull", "Ingolstadt", "Inter", "Ipswich", "Juventus",
            "La Coruna", "Las Palmas", "Lazio", "Le Havre", "Lecce", "Leeds", "Leganes", "Leicester",
            "Lens", "Levante", "Leverkusen", "Lille", "Liverpool", "Lorient", "Luton", "Lyon",
            "M'gladbach", "Mainz", "Malaga", "Mallorca", "Man City", "Man United", "Marseille",
            "Metz", "Middlesbrough", "Milan", "Monaco", "Montpellier", "Monza", "Nancy", "Nantes",
            "Napoli", "Newcastle", "Nice", "Nimes", "Norwich", "Nott'm Forest", "Nurnberg",
            "Osasuna", "Paderborn", "Palermo", "Paris SG", "Parma", "Pescara", "QPR", "RB Leipzig",
            "Real Madrid", "Reims", "Rennes", "Roma", "Salernitana", "Sampdoria", "Sassuolo",
            "Schalke 04", "Sevilla", "Sheffield United", "Sociedad", "Southampton", "Sp Gijon",
            "Spal", "Spezia", "St Etienne", "St Pauli", "Stoke", "Strasbourg", "Stuttgart",
            "Sunderland", "Swansea", "Torino", "Tottenham", "Toulouse", "Troyes", "Udinese",
            "Union Berlin", "Valencia", "Valladolid", "Vallecano", "Venezia", "Verona", "Villarreal",
            "Watford", "Werder Bremen", "West Brom", "West Ham", "Wolfsburg", "Wolves"
        ]

        self.mappings = {
            # Английская Премьер-лига
            "Manchester City": "Man City",
            "Manchester United": "Man United",
            "Manchester Utd": "Man United",
            "Man Utd": "Man United",
            "Tottenham Hotspur": "Tottenham",
            "Spurs": "Tottenham",
            "Newcastle United": "Newcastle",
            "Newcastle Utd": "Newcastle",
            "West Ham United": "West Ham",
            "West Ham Utd": "West Ham",
            "West Bromwich Albion": "West Brom",
            "WBA": "West Brom",
            "Brighton and Hove Albion": "Brighton",
            "Brighton & Hove Albion": "Brighton",
            "Wolverhampton Wanderers": "Wolves",
            "Leicester City": "Leicester",
            "Nottingham Forest": "Nott'm Forest",
            "Sheffield United": "Sheffield United",
            "AFC Bournemouth": "Bournemouth",
            "Brentford FC": "Brentford",
            "Crystal Palace": "Crystal Palace",
            "Fulham FC": "Fulham",
            "Luton Town": "Luton",
            "Everton FC": "Everton",

            # Ла Лига
            "Athletic Club": "Ath Bilbao",
            "Athletic Bilbao": "Ath Bilbao",
            "Atletico Madrid": "Ath Madrid",
            "Atlético Madrid": "Ath Madrid",
            "Real Betis": "Betis",
            "Real Sociedad": "Sociedad",
            "Celta Vigo": "Celta",
            "Rayo Vallecano": "Vallecano",
            "Espanyol": "Espanol",
            "FC Barcelona": "Barcelona",
            "Real Madrid": "Real Madrid",
            "Sevilla FC": "Sevilla",
            "Valencia CF": "Valencia",
            "Villarreal CF": "Villarreal",
            "Getafe CF": "Getafe",
            "Girona FC": "Girona",
            "Deportivo Alavés": "Alaves",
            "UD Almería": "Almeria",
            "Granada CF": "Granada",
            "UD Las Palmas": "Las Palmas",
            "RCD Mallorca": "Mallorca",
            "CA Osasuna": "Osasuna",
            "Cádiz CF": "Cadiz",

            # Бундеслига
            "Bayern München": "Bayern Munich",
            "FC Bayern München": "Bayern Munich",
            "Borussia Dortmund": "Dortmund",
            "Bayer Leverkusen": "Leverkusen",
            "Borussia Mönchengladbach": "M'gladbach",
            "Mönchengladbach": "M'gladbach",
            "Eintracht Frankfurt": "Ein Frankfurt",
            "Mainz 05": "Mainz",
            "Köln": "FC Koln",
            "FC Köln": "FC Koln",
            "1. FC Köln": "FC Koln",
            "1. FC Union Berlin": "Union Berlin",
            "Union Berlin": "Union Berlin",
            "VfL Bochum": "Bochum",
            "SV Werder Bremen": "Bremen",
            "Werder Bremen": "Bremen",
            "SV Darmstadt 98": "Darmstadt",
            "Darmstadt 98": "Darmstadt",
            "TSG Hoffenheim": "Hoffenheim",
            "1899 Hoffenheim": "Hoffenheim",
            "RB Leipzig": "RB Leipzig",
            "VfB Stuttgart": "Stuttgart",
            "VfL Wolfsburg": "Wolfsburg",
            "SC Freiburg": "Freiburg",
            "FC Augsburg": "Augsburg",
            "1. FC Heidenheim": "Heidenheim",
            "Heidenheim": "Heidenheim",

            # Серия А
            "Inter Milan": "Inter",
            "AC Milan": "Milan",
            "Inter": "Inter",
            "Milan": "Milan",
            "Juventus": "Juventus",
            "Juventus Turin": "Juventus",
            "AS Roma": "Roma",
            "Roma": "Roma",
            "SSC Napoli": "Napoli",
            "Napoli": "Napoli",
            "Atalanta BC": "Atalanta",
            "Atalanta": "Atalanta",
            "SS Lazio": "Lazio",
            "Lazio": "Lazio",
            "ACF Fiorentina": "Fiorentina",
            "Fiorentina": "Fiorentina",
            "Bologna FC": "Bologna",
            "Bologna": "Bologna",
            "Torino FC": "Torino",
            "Torino": "Torino",
            "Genoa CFC": "Genoa",
            "Genoa": "Genoa",
            "US Sassuolo": "Sassuolo",
            "Sassuolo": "Sassuolo",
            "Udinese Calcio": "Udinese",
            "Udinese": "Udinese",
            "US Salernitana": "Salernitana",
            "Salernitana": "Salernitana",
            "Hellas Verona": "Verona",
            "Verona": "Verona",
            "FC Empoli": "Empoli",
            "Empoli": "Empoli",
            "US Lecce": "Lecce",
            "Lecce": "Lecce",
            "Frosinone Calcio": "Frosinone",
            "Frosinone": "Frosinone",
            "Cagliari Calcio": "Cagliari",
            "Cagliari": "Cagliari",
            "AC Monza": "Monza",
            "Monza": "Monza",

            # Лига 1
            "Paris Saint-Germain": "Paris SG",
            "PSG": "Paris SG",
            "Paris S-G": "Paris SG",
            "Olympique Marseille": "Marseille",
            "Marseille": "Marseille",
            "Olympique Lyonnais": "Lyon",
            "Lyon": "Lyon",
            "AS Monaco": "Monaco",
            "Monaco": "Monaco",
            "LOSC Lille": "Lille",
            "Lille": "Lille",
            "Stade Rennais": "Rennes",
            "Rennes": "Rennes",
            "OGC Nice": "Nice",
            "Nice": "Nice",
            "RC Lens": "Lens",
            "Lens": "Lens",
            "Montpellier HSC": "Montpellier",
            "Montpellier": "Montpellier",
            "FC Nantes": "Nantes",
            "Nantes": "Nantes",
            "Stade de Reims": "Reims",
            "Reims": "Reims",
            "Toulouse FC": "Toulouse",
            "Toulouse": "Toulouse",
            "Strasbourg Alsace": "Strasbourg",
            "Strasbourg": "Strasbourg",
            "FC Lorient": "Lorient",
            "Lorient": "Lorient",
            "Stade Brestois": "Brest",
            "Brest": "Brest",
            "Le Havre AC": "Le Havre",
            "Le Havre": "Le Havre",
            "FC Metz": "Metz",
            "Metz": "Metz",
            "Clermont Foot": "Clermont",
            "Clermont": "Clermont"
        }

        # Ключевые слова для частичного совпадения
        self.keyword_mappings = {
            "United": "Man United",
            "City": "Man City",
            "Hotspur": "Tottenham",
            "Wanderers": "Wolves",
            "Albion": "West Brom",
            "Athletic": "Ath Bilbao",
            "Atletico": "Ath Madrid",
            "Atlético": "Ath Madrid",
            "Bayer 04": "Leverkusen",
            "Eintracht": "Ein Frankfurt",
            "Paris": "Paris SG",
        }

    def normalize_name(self, name):
        """Нормализация названия команды"""
        if not name:
            return ""

        normalized = name.strip().lower()
        normalized = re.sub(r'\b(fc|afc|cf|ssc|ac|as|us)\b', '', normalized)
        normalized = re.sub(r'\s+', ' ', normalized).strip()
        return normalized

    def map_team_name(self, api_team_name):
        """
        Преобразует название команды из API в название из датасета
        """
        if not api_team_name:
            return None

        # 1. Проверяем точные маппинги
        if api_team_name in self.mappings:
            return self.mappings[api_team_name]

        # 2. Проверяем точное совпадение с нормализацией
        normalized_api = self.normalize_name(api_team_name)
        for dataset_team in self.dataset_teams:
            if normalized_api == self.normalize_name(dataset_team):
                return dataset_team

        # 3. Проверяем частичное совпадение
        for dataset_team in self.dataset_teams:
            norm_dataset = self.normalize_name(dataset_team)
            if normalized_api in norm_dataset or norm_dataset in normalized_api:
                logger.info(f"Partial match: '{api_team_name}' -> '{dataset_team}'")
                return dataset_team

        # 4. Проверяем по ключевым словам
        for keyword, mapped_team in self.keyword_mappings.items():
            if keyword.lower() in normalized_api:
                logger.info(f"Keyword match: '{api_team_name}' -> '{mapped_team}'")
                return mapped_team

        logger.error(f"No match found for: '{api_team_name}'")
        return None

    def validate_mapping(self, home_team, away_team):
        """
        Проверяет и преобразует названия команд для прогноза
        """
        mapped_home = self.map_team_name(home_team)
        mapped_away = self.map_team_name(away_team)

        errors = []

        if not mapped_home:
            errors.append(f"Не найдено соответствие для домашней команды: '{home_team}'")

        if not mapped_away:
            errors.append(f"Не найдено соответствие для гостевой команды: '{away_team}'")

        if errors:
            return None, None, False, "; ".join(errors)

        return mapped_home, mapped_away, True, None


team_mapper = SimpleTeamMapper()
import requests
from datetime import datetime

API_TOKEN = "8b9004850ee441d7be14912d5a97a698"
BASE_URL = "https://api.football-data.org/v4"
headers = {"X-Auth-Token": API_TOKEN}


def get_team_info(team_id):
    url = f"{BASE_URL}/teams/{team_id}"
    return requests.get(url, headers=headers).json()


def get_team_matches(team_id, status="FINISHED"):
    url = f"{BASE_URL}/teams/{team_id}/matches"
    params = {"status": status}
    matches = requests.get(url, headers=headers, params=params).json().get("matches", [])
    # Сортировка по дате
    matches.sort(key=lambda m: m["utcDate"])
    return matches


def get_team_standing(team_id, competition_code):
    url = f"{BASE_URL}/competitions/{competition_code}/standings"
    data = requests.get(url, headers=headers).json()
    for table in data.get("standings", []):
        for row in table.get("table", []):
            if row["team"]["id"] == team_id:
                return row
    return None


def calc_form(matches):
    """Форма, очки, средние голы и clean sheets для последних 5 матчей"""
    last_matches = matches[-5:]  # последние 5 матчей
    stats = {"form": "", "points": 0, "wins": 0, "draws": 0, "losses": 0,
             "goals_for": 0, "goals_against": 0, "clean_sheets": 0}

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
    stats["goals_for"] /= n
    stats["goals_against"] /= n
    return stats


def calc_series(matches):
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


def calc_home_away_stats(matches):
    """Раздельная статистика дома/в гостях для последних 5 матчей"""
    last_matches = matches[-5:]
    stats = {"home": {"W":0,"D":0,"L":0,"GF":0,"GA":0,"CS":0},
             "away": {"W":0,"D":0,"L":0,"GF":0,"GA":0,"CS":0}}

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

    # Средние показатели
    for side in ["home","away"]:
        n = sum(stats[side][k] for k in ["W","D","L"])
        stats[side]["GF_avg"] = stats[side]["GF"]/n if n else 0
        stats[side]["GA_avg"] = stats[side]["GA"]/n if n else 0

    return stats


def print_team_stats(team_id, competition_code):
    team = get_team_info(team_id)
    matches = get_team_matches(team_id)

    print(f"\n=== Статистика команды: {team['name']} ===")
    print(f"Стадион: {team.get('venue')}")
    print(f"Основана: {team.get('founded')}")
    print(f"Клубные цвета: {team.get('clubColors')}")
    print(f"Веб-сайт: {team.get('website')}")

    # Позиция в таблице
    standing = get_team_standing(team_id, competition_code)
    if standing:
        print(f"\nПозиция в таблице: {standing['position']} из {standing['playedGames']}")
        print(f"Очки: {standing['points']}, W/D/L: {standing['won']}/{standing['draw']}/{standing['lost']}, ГЗ/ПЗ: {standing['goalsFor']}/{standing['goalsAgainst']}")

    # Форма и общие показатели
    form_stats = calc_form(matches)
    print("\n=== Последние 5 матчей ===")
    print(f"Форма: {form_stats['form']}")
    print(f"Очки за 5 матчей: {form_stats['points']}")
    print(f"Средние голы забитые: {form_stats['goals_for']:.2f}, пропущенные: {form_stats['goals_against']:.2f}")
    print(f"Clean sheets: {form_stats['clean_sheets']}")

    # Серии
    series = calc_series(matches)
    print(f"\nСерия без поражений: {series['unbeaten']}")
    print(f"Победная серия: {series['win_streak']}")

    # Раздельная статистика
    home_away = calc_home_away_stats(matches)
    print("\n=== Раздельная статистика дома/в гостях (последние 5 матчей) ===")
    for side in ["home","away"]:
        s = home_away[side]
        print(f"\n{side.capitalize()}: W/D/L: {s['W']}/{s['D']}/{s['L']}, GF/GA: {s['GF']}/{s['GA']}, GF_avg: {s['GF_avg']:.2f}, GA_avg: {s['GA_avg']:.2f}, Clean sheets: {s['CS']}")

    # Последние 5 матчей с результатами
    print("\nПоследние матчи:")
    for m in matches[-5:]:
        dt = datetime.fromisoformat(m["utcDate"].replace("Z", "+00:00"))
        home = m["homeTeam"]["name"]
        away = m["awayTeam"]["name"]
        score = m["score"]["fullTime"]
        print(f"{dt:%Y-%m-%d} — {home} {score['home']}:{score['away']} {away}")


# === Пример использования ===
if __name__ == "__main__":
    team_id = 66  # Manchester United
    competition_code = "PL"  # Premier League
    print_team_stats(team_id, competition_code)

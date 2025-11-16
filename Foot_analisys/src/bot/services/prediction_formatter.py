"""
Форматирование прогнозов для разных типов отчетов
"""

def format_quick_prediction(result: dict) -> str:
    """Форматирует быстрый прогноз"""
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
    elif goal_diff < -0.5:
        away_prob = min(85, 50 - goal_diff * 15)
        home_prob = max(5, 20 + goal_diff * 10)
    else:
        home_prob = 35
        away_prob = 35

    draw_prob = 100 - home_prob - away_prob

    report = f"""
⚡ <b>Быстрый прогноз</b>

🏠 {home_team} vs ✈️ {away_team}

<b>Прогноз счета:</b> {score}
<b>Вероятности:</b>
  🏠 Победа хозяев: {home_prob:.0f}%
  🤝 Ничья: {draw_prob:.0f}%  
  ✈️ Победа гостей: {away_prob:.0f}%

💡 <i>Матч выбран из актуального расписания</i>
"""
    return report

def format_detailed_prediction(result: dict) -> str:
    """Форматирует детальный прогноз в старом стиле"""
    predictions = result['predictions']
    home_team = result['home_team']
    away_team = result['away_team']

    home_goals = round(predictions.get('Target_FTHG', 1.5), 1)
    away_goals = round(predictions.get('Target_FTAG', 1.2), 1)
    score = f"{int(round(home_goals))}:{int(round(away_goals))}"

    # Вероятности
    goal_diff = home_goals - away_goals
    if goal_diff > 0.5:
        result_text = "Победа хозяев"
        home_prob = min(85, 50 + goal_diff * 15)
        away_prob = max(5, 20 - goal_diff * 10)
    elif goal_diff < -0.5:
        result_text = "Победа гостей"
        away_prob = min(85, 50 - goal_diff * 15)
        home_prob = max(5, 20 + goal_diff * 10)
    else:
        result_text = "🤝 Ничья"
        home_prob = 35
        away_prob = 35

    draw_prob = 100 - home_prob - away_prob

    # Статистика
    home_shots = round(predictions.get('Target_HS', 10), 1)
    away_shots = round(predictions.get('Target_AS', 8), 1)
    home_shots_target = round(predictions.get('Target_HST', 4), 1)
    away_shots_target = round(predictions.get('Target_AST', 3), 1)
    home_corners = round(predictions.get('Target_HC', 5), 1)
    away_corners = round(predictions.get('Target_AC', 4), 1)
    home_fouls = round(predictions.get('Target_HF', 12), 1)
    away_fouls = round(predictions.get('Target_AF', 11), 1)
    home_yellows = round(predictions.get('Target_HY', 2), 1)
    away_yellows = round(predictions.get('Target_AY', 2), 1)
    home_reds = round(predictions.get('Target_HR', 0), 1)
    away_reds = round(predictions.get('Target_AR', 0), 1)

    report = f"""
⚽️ <b>ПРОГНОЗ МАТЧА</b>

🏠 {home_team} vs ✈️ {away_team}

━━━━━━━━━━━━━━━━━━━━━━━━
🎯 <b>ОСНОВНОЙ ПРОГНОЗ</b>

Счет: {score}
Результат: {result_text}

Вероятности:
  🏠 Победа хозяев: {home_prob:.0f}%
  🤝 Ничья: {draw_prob:.0f}%
  ✈️ Победа гостей: {away_prob:.0f}%

━━━━━━━━━━━━━━━━━━━━━━━━
📊 <b>СТАТИСТИКА</b>

⚽️ Голы: {home_goals:.1f} - {away_goals:.1f}
🎯 Удары: {home_shots:.0f} - {away_shots:.0f}
🔵 В створ: {home_shots_target:.0f} - {away_shots_target:.0f}
🚩 Угловые: {home_corners:.0f} - {away_corners:.0f}
⚠️ Фолы: {home_fouls:.0f} - {away_fouls:.0f}
🟨 Желтые: {home_yellows:.0f} - {away_yellows:.0f}
🟥 Красные: {home_reds:.0f} - {away_reds:.0f}
"""

    return report
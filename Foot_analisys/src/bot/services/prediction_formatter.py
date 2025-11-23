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


# services/prediction_formatter.py - БЕЗ ОКРУГЛЕНИЯ

def format_detailed_prediction(result: dict) -> str:
    """Форматирует детальный прогноз БЕЗ округления"""
    predictions = result['predictions']
    home_team = result['home_team']
    away_team = result['away_team']

    # БЕЗ ОКРУГЛЕНИЯ - используем оригинальные значения
    home_goals = predictions.get('Target_FTHG', 1.5)
    away_goals = predictions.get('Target_FTAG', 1.2)

    # Для счета используем математическое округление к ближайшему целому
    home_goals_int = round(home_goals)
    away_goals_int = round(away_goals)
    score = f"{home_goals_int}:{away_goals_int}"

    # Правильное определение результата
    if home_goals > away_goals:
        result_text = "Победа хозяев"
    elif away_goals > home_goals:
        result_text = "Победа гостей"
    else:
        result_text = "🤝 Ничья"

    # Вероятности (оставляем вашу текущую логику)
    goal_diff = home_goals - away_goals

    # Базовые вероятности для равных команд
    base_home = 45  # Домашнее преимущество
    base_away = 30  # Гостевой недостаток
    base_draw = 25  # Базовая ничья

    # Корректируем на разницу голов (симметрично)
    adjustment = goal_diff * 10  # 10% за каждый гол разницы

    home_prob = max(5, min(85, base_home + adjustment))
    away_prob = max(5, min(85, base_away - adjustment))

    # Пересчитываем ничью чтобы сумма была 100%
    draw_prob = 100 - home_prob - away_prob

    # Если ничья вышла за границы, корректируем
    if draw_prob < 5:
        draw_prob = 5
        # Перераспределяем оставшиеся 95% пропорционально
        total = home_prob + away_prob
        home_prob = (home_prob / total) * 95
        away_prob = (away_prob / total) * 95
    elif draw_prob > 40:
        draw_prob = 40
        total = home_prob + away_prob
        home_prob = (home_prob / total) * 60
        away_prob = (away_prob / total) * 60

    home_prob = round(home_prob)
    draw_prob = round(draw_prob)
    away_prob = round(away_prob)

    # Статистика БЕЗ ОКРУГЛЕНИЯ
    home_shots = predictions.get('Target_HS', 10)
    away_shots = predictions.get('Target_AS', 8)
    home_shots_target = predictions.get('Target_HST', 4)
    away_shots_target = predictions.get('Target_AST', 3)
    home_corners = predictions.get('Target_HC', 5)
    away_corners = predictions.get('Target_AC', 4)
    home_fouls = predictions.get('Target_HF', 12)
    away_fouls = predictions.get('Target_AF', 11)
    home_yellows = predictions.get('Target_HY', 2)
    away_yellows = predictions.get('Target_AY', 2)
    home_reds = predictions.get('Target_HR', 0)
    away_reds = predictions.get('Target_AR', 0)

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

⚽️ Голы: {home_goals:.3f} - {away_goals:.3f}
🎯 Удары: {home_shots:.3f} - {away_shots:.3f}
🔵 В створ: {home_shots_target:.3f} - {away_shots_target:.3f}
🚩 Угловые: {home_corners:.3f} - {away_corners:.3f}
⚠️ Фолы: {home_fouls:.3f} - {away_fouls:.3f}
🟨 Желтые: {home_yellows:.3f} - {away_yellows:.3f}
🟥 Красные: {home_reds:.3f} - {away_reds:.3f}
"""

    return report
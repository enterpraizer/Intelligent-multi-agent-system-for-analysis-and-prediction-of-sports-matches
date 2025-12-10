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
    """Форматирует детальный прогноз с пояснениями, опираясь на ОКРУГЛЁННЫЙ счёт"""
    predictions = result['predictions']
    home_team = result['home_team']
    away_team = result['away_team']

    # Сырые ожидания модели
    home_goals_raw = float(predictions.get('Target_FTHG', 1.5))
    away_goals_raw = float(predictions.get('Target_FTAG', 1.2))

    # ОКРУГЛЁННЫЙ счёт — главный для результата
    home_goals_int = int(round(home_goals_raw))
    away_goals_int = int(round(away_goals_raw))
    score = f"{home_goals_int}:{away_goals_int}"

    # Результат и голевая разница считаются по ОКРУГЛЁННЫМ голам
    if home_goals_int > away_goals_int:
        result_text = "Победа хозяев"
    elif away_goals_int > home_goals_int:
        result_text = "Победа гостей"
    else:
        result_text = "🤝 Ничья"

    goal_diff_int = home_goals_int - away_goals_int

    # Базовые вероятности для равных команд
    base_home = 45.0
    base_away = 30.0
    base_draw = 25.0

    # Корректировка на разницу ОКРУГЛЁННЫХ голов
    adjustment = goal_diff_int * 10.0  # 10% за гол разницы

    home_prob = base_home + adjustment
    away_prob = base_away - adjustment
    draw_prob = base_draw

    # Ограничения 5–85% и базовый диапазон для ничьей
    home_prob = min(85.0, max(5.0, home_prob))
    away_prob = min(85.0, max(5.0, away_prob))
    draw_prob = max(5.0, min(70.0, draw_prob))

    # Нормализация до 100%
    total = home_prob + away_prob + draw_prob
    home_prob = home_prob / total * 100.0
    away_prob = away_prob / total * 100.0
    draw_prob = draw_prob / total * 100.0

    home_prob = round(home_prob)
    draw_prob = round(draw_prob)
    away_prob = round(away_prob)

    # Остальная статистика по сырым значениям
    home_shots = float(predictions.get('Target_HS', 10))
    away_shots = float(predictions.get('Target_AS', 8))
    home_shots_target = float(predictions.get('Target_HST', 4))
    away_shots_target = float(predictions.get('Target_AST', 3))
    home_corners = float(predictions.get('Target_HC', 5))
    away_corners = float(predictions.get('Target_AC', 4))
    home_fouls = float(predictions.get('Target_HF', 12))
    away_fouls = float(predictions.get('Target_AF', 11))
    home_yellows = float(predictions.get('Target_HY', 2))
    away_yellows = float(predictions.get('Target_AY', 2))
    home_reds = float(predictions.get('Target_HR', 0))
    away_reds = float(predictions.get('Target_AR', 0))

    home_shot_acc = home_shots_target / max(home_shots, 1.0) * 100.0
    away_shot_acc = away_shots_target / max(away_shots, 1.0) * 100.0

    # Ключевые моменты
    moments = []
    total_goals = home_goals_raw + away_goals_raw
    total_shots = home_shots + away_shots
    total_fouls = home_fouls + away_fouls
    total_yellows = home_yellows + away_yellows
    total_corners = home_corners + away_corners

    if total_goals > 3:
        moments.append(f"• Ожидается результативный матч (≈ {total_goals:.1f} гола).")
    elif total_goals < 2:
        moments.append("• Ожидается низкая результативность и осторожная игра.")

    if total_shots > 20:
        moments.append(f"• Обе команды создадут много моментов (≈ {total_shots:.0f} ударов).")

    if home_shot_acc > 50:
        moments.append(f"• {home_team} будет точен в ударах (≈ {home_shot_acc:.0f}% в створ).")
    if away_shot_acc > 50:
        moments.append(f"• {away_team} будет точен в ударах (≈ {away_shot_acc:.0f}% в створ).")

    if total_fouls > 22:
        moments.append(f"• Напряжённый матч с большим количеством фолов (≈ {total_fouls:.0f}).")

    if total_yellows > 4:
        moments.append(f"• Ожидается много жёлтых карточек (≈ {total_yellows:.0f}).")

    if home_reds + away_reds >= 0.5:
        moments.append("• Есть риск удаления игрока.")

    if total_corners > 10:
        moments.append(f"• Предполагается много угловых (≈ {total_corners:.0f}).")

    key_moments_text = "\n".join(moments) if moments else "• Существенных аномалий по статистике не ожидается."

    # Краткий анализ
    expert_parts = []
    if goal_diff_int > 1:
        expert_parts.append(
            f"{home_team} выглядят явным фаворитом и имеют хорошие шансы на уверенную победу ({score})."
        )
    elif goal_diff_int < -1:
        expert_parts.append(
            f"{away_team} выглядят сильнее и способны выиграть матч ({score})."
        )
    elif goal_diff_int == 0:
        expert_parts.append(
            "Ожидается равный матч: прогнозируется ничья и плотный счёт."
        )
    else:
        expert_parts.append(
            "Команды близки по уровню, ожидается упорная борьба с минимальной разницей в счёте."
        )

    if total_goals > 3:
        expert_parts.append("Игра, вероятно, будет открытой и результативной.")
    elif total_goals < 2:
        expert_parts.append("Возможна закрытая тактическая игра с небольшим числом голов.")

    if total_shots > 20:
        expert_parts.append("Количество ударов говорит о высокой интенсивности в атаке.")

    expert_text = " ".join(expert_parts)

    report = f"""
⚽️ <b>ПРОГНОЗ МАТЧА</b>

🏠 {home_team} vs ✈️ {away_team}

━━━━━━━━━━━━━━━━━━━━━━━━
🎯 <b>ОСНОВНОЙ ПРОГНОЗ</b>

Счёт: {score}
Результат: {result_text}

Вероятности:
  🏠 Победа хозяев: {home_prob:.0f}%
  🤝 Ничья: {draw_prob:.0f}%
  ✈️ Победа гостей: {away_prob:.0f}%

━━━━━━━━━━━━━━━━━━━━━━━━
📊 <b>СТАТИСТИКА (ожидания модели)</b>

⚽️ Голы (сырые): {home_goals_raw:.3f} — {away_goals_raw:.3f}
🎯 Удары: {home_shots:.3f} — {away_shots:.3f}
🔵 В створ: {home_shots_target:.3f} — {away_shots_target:.3f}
🎯 Точность ударов: {home_shot_acc:.1f}% — {away_shot_acc:.1f}%
🚩 Угловые: {home_corners:.3f} — {away_corners:.3f}
⚠️ Фолы: {home_fouls:.3f} — {away_fouls:.3f}
🟨 Жёлтые: {home_yellows:.3f} — {away_yellows:.3f}
🟥 Красные: {home_reds:.3f} — {away_reds:.3f}

━━━━━━━━━━━━━━━━━━━━━━━━
⚡️ <b>КЛЮЧЕВЫЕ МОМЕНТЫ</b>

{key_moments_text}

━━━━━━━━━━━━━━━━━━━━━━━━
💡 <b>КРАТКИЙ АНАЛИЗ</b>

{expert_text}
"""

    return report

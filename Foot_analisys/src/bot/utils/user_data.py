"""
Утилиты для работы с пользовательскими данными
"""
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

# Хранилище пользовательских данных (временное, лучше использовать базу данных)
user_data_store = {}


def get_user_data(user_id):
    """Получение данных пользователя"""
    if user_id not in user_data_store:
        user_data_store[user_id] = {
            'favorite_teams': [],  # Список ID избранных команд
            'notifications': {
                'enabled': True,
                'time_before_match': 24,  # часов до матча
                'match_reminders': True,
                'prediction_reminders': True
            },
            'scheduled_matches': [],  # матчи для уведомлений
            'prediction_history': [],
            'user_predictions': []
        }
    return user_data_store[user_id]


def save_user_prediction(user_id, home_team, away_team, user_score, actual_score=None):
    """Сохранение пользовательского прогноза"""
    user_data = get_user_data(user_id)
    prediction = {
        'timestamp': datetime.now(),
        'home_team': home_team,
        'away_team': away_team,
        'user_prediction': user_score,
        'actual_score': actual_score,
        'is_correct': None
    }
    user_data['user_predictions'].append(prediction)


def add_favorite_team(user_id, team_id, team_name):
    """Добавление команды в избранное"""
    user_data = get_user_data(user_id)

    # Проверяем, не добавлена ли уже команда
    for fav_team in user_data['favorite_teams']:
        if fav_team['id'] == team_id:
            return False  # Команда уже в избранном

    # Добавляем команду
    user_data['favorite_teams'].append({
        'id': team_id,
        'name': team_name,
        'added_date': datetime.now()
    })

    return True


def remove_favorite_team(user_id, team_id):
    """Удаление команды из избранного"""
    user_data = get_user_data(user_id)

    # Ищем команду для удаления
    for i, fav_team in enumerate(user_data['favorite_teams']):
        if fav_team['id'] == team_id:
            user_data['favorite_teams'].pop(i)
            return True

    return False  # Команда не найдена в избранном


def get_favorite_teams(user_id):
    """Получение списка избранных команд"""
    user_data = get_user_data(user_id)
    return user_data['favorite_teams']


def is_team_favorite(user_id, team_id):
    """Проверка, является ли команда избранной"""
    user_data = get_user_data(user_id)
    return any(fav_team['id'] == team_id for fav_team in user_data['favorite_teams'])


def update_notification_settings(user_id, enabled=None, time_before_match=None,
                                 match_reminders=None, prediction_reminders=None):
    """Обновление настроек уведомлений"""
    user_data = get_user_data(user_id)

    if enabled is not None:
        user_data['notifications']['enabled'] = enabled
    if time_before_match is not None:
        user_data['notifications']['time_before_match'] = time_before_match
    if match_reminders is not None:
        user_data['notifications']['match_reminders'] = match_reminders
    if prediction_reminders is not None:
        user_data['notifications']['prediction_reminders'] = prediction_reminders

    return user_data['notifications']


def get_notification_settings(user_id):
    """Получение настроек уведомлений"""
    user_data = get_user_data(user_id)
    return user_data['notifications']


def add_scheduled_match(user_id, match_data):
    """Добавление матча для уведомлений"""
    user_data = get_user_data(user_id)

    # Проверяем, не добавлен ли уже матч
    for match in user_data['scheduled_matches']:
        if (match['match_id'] == match_data.get('match_id') and
                match['home_team'] == match_data.get('home_team') and
                match['away_team'] == match_data.get('away_team')):
            return False

    user_data['scheduled_matches'].append({
        'match_id': match_data.get('match_id'),
        'home_team': match_data.get('home_team'),
        'away_team': match_data.get('away_team'),
        'match_time': match_data.get('match_time'),
        'league': match_data.get('league'),
        'notification_sent': False,
        'added_date': datetime.now()
    })

    return True


def get_scheduled_matches(user_id):
    """Получение списка запланированных матчей для уведомлений"""
    user_data = get_user_data(user_id)
    return user_data['scheduled_matches']


def mark_notification_sent(user_id, match_id):
    """Отметка, что уведомление отправлено"""
    user_data = get_user_data(user_id)

    for match in user_data['scheduled_matches']:
        if match['match_id'] == match_id:
            match['notification_sent'] = True
            match['sent_date'] = datetime.now()
            return True

    return False


def cleanup_old_matches(user_id):
    """Очистка старых матчей (после их завершения)"""
    user_data = get_user_data(user_id)
    current_time = datetime.now()

    # Удаляем матчи, которые прошли более 2 дней назад
    user_data['scheduled_matches'] = [
        match for match in user_data['scheduled_matches']
        if match.get('match_time') and
           (match['match_time'] - current_time).days > -2
    ]


def get_all_users_with_notifications():
    """Получение всех пользователей с включенными уведомлениями"""
    return {
        user_id: user_data
        for user_id, user_data in user_data_store.items()
        if user_data.get('notifications', {}).get('enabled', False)
    }
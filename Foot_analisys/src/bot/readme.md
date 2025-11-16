### Обработчики (handlers/)
- **`main_handler.py`** - Главный маршрутизатор callback-ов
- **`menu_handlers.py`** - Навигация по меню
- **`prediction_handlers.py`** - Прогнозы матчей
- **`stats_handlers.py`** - Статистика команд
- **`schedule_handlers.py`** - Расписание матчей
- **`favorites_handlers.py`** - Избранные команды
- **`settings_handlers.py`** - Настройки уведомлений
- **`user_handlers.py`** - История прогнозов
- **`about_handlers.py`** - Информация о боте

### Сервисы (services/)
- **`team_stats_service.py`** - Работа с Football-data.org API
- **`schedule_service.py`** - Получение расписания матчей
- **`team_mapper.py`** - Маппинг названий команд между API и датасетом
- **`llm_analysis_service.py`** - AI-анализ через DeepSeek
- **`notification_service.py`** - Система умных уведомлений
- **`prediction_formatter.py`** - Форматирование прогнозов

### Утилиты (utils/)
- **`user_data.py`** - Временное хранилище пользовательских данных
- **`messages.py`** - Текстовые шаблоны и сообщения


### 🔌 Внешние API

- **Football-data.org**

База URL: https://api.football-data.org/v4
Ключ: 8b9004850ee441d7be14912d5a97a698
Эндпоинты:
GET /teams/{id} - информация о команде
GET /teams/{id}/matches - матчи команды
GET /competitions/{code}/matches - матчи лиги
GET /competitions/{code}/standings - таблица


- **OpenRouter AI**

База URL: https://openrouter.ai/api/v1
Модель: tngtech/deepseek-r1t2-chimera:free
Функция: Глубокий анализ матчей


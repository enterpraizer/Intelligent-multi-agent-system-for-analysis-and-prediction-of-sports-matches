# send_test_message.py
"""
Скрипт для принудительной отправки тестового сообщения в бот
"""

import asyncio
import os
import sys
from telegram import Bot
from telegram.error import TelegramError

# Токен вашего бота
BOT_TOKEN = "8144016399:AAF_Ww1EJXRNQPMlAzPq1jE2ni40dm9o94s"

# ID чата куда отправлять (ваш ID или ID группы)
CHAT_ID = "ВАШ_CHAT_ID"  # Замените на ваш chat_id


async def send_test_message():
    """Отправляет тестовое сообщение"""
    try:
        bot = Bot(token=BOT_TOKEN)

        # Первое сообщение - прогноз
        message1 = """
⚽️ ПРОГНОЗ МАТЧА

🏠 Arsenal vs ✈️ Tottenham

━━━━━━━━━━━━━━━━━━━━━━━━
🎯 ОСНОВНОЙ ПРОГНОЗ

Счет: 2:0
Результат: Победа гостей

Вероятности:
  🏠 Победа хозяев: 61%
  🤝 Ничья: 22%
  ✈️ Победа гостей: 17%

━━━━━━━━━━━━━━━━━━━━━━━━
📊 СТАТИСТИКА

⚽️ Голы: 1.560 - 0.433
🎯 Удары: 5.589 - 3.997
🔵 В створ: 4.597 - 2.345
🚩 Угловые: 2.148 - 2.217
⚠️ Фолы: 0.547 - 2.387
🟨 Желтые: 0.341 - 1.541
🟥 Красные: 0.312 - 0.411
"""

        # Второе сообщение - предложение оставить прогноз
        message2 = """
🤔 Не хотите ли оставить свой прогноз?

Мой прогноз: 2:0
"""

        print("📤 Отправляю сообщения...")

        # Отправляем первое сообщение
        await bot.send_message(
            chat_id=CHAT_ID,
            text=message1,
            parse_mode='HTML'
        )
        print("✅ Первое сообщение отправлено")

        # Ждем секунду
        await asyncio.sleep(1)

        # Отправляем второе сообщение
        await bot.send_message(
            chat_id=CHAT_ID,
            text=message2,
            parse_mode='HTML'
        )
        print("✅ Второе сообщение отправлено")

        print("🎉 Все сообщения успешно отправлены!")

    except TelegramError as e:
        print(f"❌ Ошибка Telegram: {e}")
    except Exception as e:
        print(f"❌ Общая ошибка: {e}")


def get_chat_id():
    """Получить chat_id если не указан"""

    async def _get_updates():
        bot = Bot(token=BOT_TOKEN)
        updates = await bot.get_updates()
        if updates:
            for update in updates:
                if update.message:
                    return update.message.chat_id
        return None

    return asyncio.run(_get_updates())


if __name__ == "__main__":
    # Если chat_id не указан, пытаемся получить автоматически
    if CHAT_ID == "ВАШ_CHAT_ID":
        print("🔍 Получаю chat_id автоматически...")
        chat_id = get_chat_id()
        if chat_id:
            print(f"✅ Найден chat_id: {chat_id}")
            # Создаем временную копию с правильным chat_id
            with open('send_test_message_temp.py', 'w', encoding='utf-8') as f:
                f.write(f'BOT_TOKEN = "{BOT_TOKEN}"\n')
                f.write(f'CHAT_ID = "{chat_id}"\n')
                f.write(open(__file__).read().split('if __name__ == "__main__":')[0])
                f.write('\nif __name__ == "__main__":\n    asyncio.run(send_test_message())')

            print("📝 Создан файл send_test_message_temp.py с вашим chat_id")
            print("🚀 Запустите: python send_test_message_temp.py")
        else:
            print("❌ Не удалось найти chat_id. Напишите боту сообщение и попробуйте снова.")
    else:
        # Запускаем отправку
        asyncio.run(send_test_message())
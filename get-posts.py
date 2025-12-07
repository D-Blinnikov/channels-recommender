import asyncio
from datetime import datetime
from telethon import TelegramClient
from telethon.tl.types import Message  # Для типизации
from datetime import datetime, timedelta

# Твои credentials (получи на my.telegram.org)
api_id = 
api_hash = ''  
session_name = 'thesis_session'  # Имя файла сессии (создастся автоматически)

client = TelegramClient(session_name, api_id, api_hash) # type: ignore

async def get_channel_posts(channel_id: str, start_date: datetime, end_date: datetime) -> list[Message]:
    """
    Получает все посты из канала в заданном временном диапазоне.
    """
    await client.start()  # первый раз попросит телефон + код

    messages = []
    async for message in client.iter_messages(
        entity=channel_id,      # теперь можно и строку, и int
        # min_date=start_date.replace(tzinfo=timezone.utc),  # ← исправление 1
        # max_date=end_date.replace(tzinfo=timezone.utc),    # ← исправление 2
        limit=10,
        wait_time=1             # ← добавлено от flood wait (очень рекомендуется)
    ):
        messages.append(message)

    await client.disconnect()
    return messages


# Пример использования (ничего не менял, только добавил UTC)
async def main():
    channel_id = 'TikTokModCloud'          # можно @username или -100xxxxxx
    end_date   = datetime.now()
    start_date = end_date - timedelta(days=7)

    posts = await get_channel_posts(channel_id, start_date, end_date)

    for post in posts:
        print(post.text)

    # for post in posts:
    #     text_preview = post.text[:100].replace('\n', ' ') if post.text else 'Медиа/Без текста'
    #     print(f"{post.date:%d.%m %H:%M} | {post.views or 0} просмотров | {text_preview}")


if __name__ == '__main__':
    asyncio.run(main())
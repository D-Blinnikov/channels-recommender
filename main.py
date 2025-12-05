import os
import requests
from time import sleep
from dotenv import load_dotenv

load_dotenv()

TGSTAT_TOKEN = os.environ.get("TGSTAT_TOKEN")

BASE_URL = "https://api.tgstat.ru"



def api(method: str, params):
    if params is None:
        params = {}

    url = f"{BASE_URL}/{method}"
    params_with_token = {"token": TGSTAT_TOKEN, **params}

    r = requests.get(url, params=params_with_token)
    data = r.json()

    print('data:', data)

    return data['response']


# 1) Получить категории
def get_categories():
    return api("database/categories", {})


# 2) Найти каналы по категории
def search_channels_by_category(category: str, limit: int = 100):
    return api(
        "channels/search",
        {
            "category": category,
            "limit": limit,
        }
    )


# 3) Инфо о канале
def get_channel_info(channel_id: str):
    return api("channels/get", {"channelId": channel_id})


# 4) Посты канала
def get_channel_posts(channel_id: str, limit: int = 200):
    return api("channels/posts", {
        "channelId": channel_id,
        "limit": limit
    })


# -------------------------------------------------------------------------
# Сбор датасета
# -------------------------------------------------------------------------

def run():
    print("Получаю категории…")
    categories = get_categories()

    print('categories:', categories)

    cat_names = []

    for cat in categories:
        cat_names.append(cat['code'])
        print(cat['code'])

    # Чтобы не рвать API, ограничимся первыми 5 категориями
    for cat in categories[:3]:
        print(f"\nКатегория: {cat}")

        channels = search_channels_by_category(cat, limit=1)

        for ch in channels.get("items", []):
            print('Chanel:', ch)
            channel_id = ch.get("id") or ch.get("username")
            # print(f"   Канал: {channel_id}")

            # 1) Информация о канале
            # info = get_channel_info(channel_id)
            # тут ты бы сохранил в БД
            # save_channel(info)

            # 2) Посты
            # posts = get_channel_posts(channel_id, limit=1)
            # print('found posts:', posts)
            # items = posts.get("items", [])

            # print(f"      Скачано постов: {len(items)}")

            # save_posts(channel_id, items)

            # Чтобы не выглядеть как бот-маньяк
            sleep(0.5)


if __name__ == "__main__":
    run()

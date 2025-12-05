# wb_parser.py — обновлённая версия для Wildberries (2025)
import requests
from bs4 import BeautifulSoup
import re
import time

def get_wb_query(url: str) -> str:
    """
    Парсит страницу Wildberries → возвращает готовый query для семантического поиска
    Пример: "Зимний комбинезон Reima для девочек, рост 104 см, цвет тёмно-синий. Бренд: Reima | Материал: полиэстер | Утеплитель: синтетический"
    """
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36",
        "Accept-Language": "ru-RU,ru;q=0.9,en;q=0.8",
        "Referer": "https://www.wildberries.ru/"
    }

    try:
        r = requests.get(url, headers=headers, timeout=20)
        r.raise_for_status()
    except Exception as e:
        return f"Ошибка загрузки: {e}"

    soup = BeautifulSoup(r.text, "html.parser")

    # 1. Название товара (h1 или meta og:title)
    title = ""
    title_tag = soup.find("h1", class_=re.compile(r"product-name|title")) or soup.find("meta", property="og:title")
    if title_tag:
        title = title_tag.get_text(strip=True) if title_tag.name == "h1" else title_tag.get("content", "")
    title = re.sub(r"^\d+\s*", "", title).strip()  # убираем артикул в начале

    # 2. Бренд (специальный блок или в характеристиках)
    brand = "N/A"
    brand_tag = soup.find("a", {"data-link": "text{:productBrand}"}) or soup.find("span", string=re.compile(r"Бренд[:\s]", re.I))
    if brand_tag:
        brand = brand_tag.get_text(strip=True)
    elif "бренд" in title.lower():
        brand = re.search(r"бренд[:\s]*([А-Яа-яЁёA-Za-z]+)", title, re.I).group(1) if re.search(r"бренд[:\s]*([А-Яа-яЁёA-Za-z]+)", title, re.I) else "N/A"

    # 3. Характеристики (таблица или список li/div с классами params/details)
    specs = []
    # Основной блок характеристик (новый дизайн 2025)
    params_block = soup.find("div", class_=re.compile(r"product-params|characteristics|collapsable|params-list"))
    if params_block:
        for row in params_block.find_all(["div", "li"], class_=re.compile(r"row|item|param")):
            key = row.find(["span", "div"], string=re.compile(r"бренд|цвет|размер|материал|сезон|состав|рост|пол|утеплитель|водонепроницаемость", re.I))
            value = row.get_text(strip=True) if key else None
            if key and value:
                specs.append(f"{key.get_text(strip=True).lower().rstrip(':')}: {value}")

    # Запасной вариант — старый дизайн (li в ul)
    if not specs:
        ul = soup.find("ul", class_=re.compile(r"details|params"))
        if ul:
            for li in ul.find_all("li"):
                text = li.get_text(separator=": ", strip=True)
                if ":" in text and any(kw in text.lower() for kw in ["цвет", "размер", "материал", "сезон", "рост", "пол"]):
                    specs.append(text)

    # 4. Собираем query
    parts = [title]
    if brand != "N/A" and brand not in title:
        parts.insert(0, brand)

    query = " ".join(parts)

    if specs:
        specs_text = " | ".join(specs[:8])  # не больше 8, чтобы не перегружать
        query += ". " + specs_text

    # Чистка
    query = re.sub(r"\s+", " ", query).strip()
    query = re.sub(r"\| \|+", " | ", query)
    query = query.replace("•", "").replace("\n", " ")

    return query if query else "Не удалось извлечь данные"


# ====================== ТЕСТ НА ТВОЕЙ ССЫЛКЕ ======================
url = "https://www.wildberries.ru/catalog/181727564/detail.aspx"
# url = 'https://www.cifrus.ru/description/1/huawei_nova_14_12_256gb_4g_white_51098law_rst/harakteristiki#tab-specification'

print(f"Парсим: {url}")
query = get_wb_query(url)
print(f"Готовый query: {query}")
print(f"\nДлина: {len(query)} символов")
time.sleep(1)  # пауза для этичности
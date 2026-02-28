import re
import emoji  # Убедитесь, что emoji установлен в вашем окружении

def clean_text(text: str, remove_emojis: bool = True,
                    remove_urls: bool = True,
                    remove_mentions: bool = True,
                    remove_hashtags: bool = False,
                    remove_extra_spaces: bool = True,
                    remove_special_chars: bool = False) -> str:
    """
    Очищает текст поста от нежелательных элементов.
    
    Args:
        text: исходный текст
        remove_emojis: удалять эмодзи/смайлики
        remove_urls: удалять URL ссылки
        remove_mentions: удалять упоминания (@username)
        remove_hashtags: удалять хэштеги (#тег)
        remove_extra_spaces: удалять лишние пробелы
        remove_special_chars: удалять специальные символы (оставить только буквы/цифры/пробелы)
       
    Returns:
        str: очищенный текст
    """
    if not isinstance(text, str):
        return ""
    
    cleaned = text
    replacement = ' '
    
    # 1. Удаление эмодзи и смайликов
    if remove_emojis:
        # Используем библиотеку emoji для удаления эмодзи
        cleaned = emoji.replace_emoji(cleaned, replacement)
       
        # Дополнительно удаляем常见ные символы эмодзи (на всякий случай)
        emoji_pattern = re.compile("["
            u"\U0001F600-\U0001F64F"  # эмоции
            u"\U0001F300-\U0001F5FF"  # символы и пиктограммы
            u"\U0001F680-\U0001F6FF"  # транспорт и символы
            u"\U0001F1E0-\U0001F1FF"  # флаги
            u"\U00002702-\U000027B0"  # различные символы
            u"\U000024C2-\U0001F251"  # дополнительные
            u"\U0001F900-\U0001F9FF"  # дополнительные эмодзи
            u"\U0001FA70-\U0001FAFF"  # дополнительные эмодзи
            u"\U00002600-\U000026FF"  # различные символы
            u"\U00002700-\U000027BF"  # символы Dingbats
            "]+", flags=re.UNICODE)
        cleaned = emoji_pattern.sub(replacement, cleaned)
    
    # 2. Удаление URL
    if remove_urls:
        url_pattern = re.compile(r'https?://\S+|www\.\S+')
        cleaned = url_pattern.sub(replacement, cleaned)
    
    # 3. Удаление упоминаний (@username)
    if remove_mentions:
        mention_pattern = re.compile(r'@\w+')
        cleaned = mention_pattern.sub(replacement, cleaned)
    
    # 4. Удаление хэштегов
    if remove_hashtags:
        hashtag_pattern = re.compile(r'#\w+')
        cleaned = hashtag_pattern.sub(replacement, cleaned)
    
    # 5. Удаление специальных символов (оставляем только буквы, цифры и пробелы)
    if remove_special_chars:
        # Оставляем кириллицу, латиницу, цифры и пробелы
        special_chars_pattern = re.compile(r'[^а-яА-Яa-zA-Z0-9\s]')
        cleaned = special_chars_pattern.sub(replacement, cleaned)
    
    # 6. Удаление лишних пробелов
    if remove_extra_spaces:
        # Заменяем множественные пробелы на один
        cleaned = re.sub(r'\s+', replacement, cleaned)
        # Удаляем пробелы в начале и конце
        cleaned = cleaned.strip()
    
    return cleaned
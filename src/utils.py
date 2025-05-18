import json

from typing import Optional, Dict
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

def load_json_data(path: str) -> Optional[Dict]:
    """Загрузка данных о намерениях пользователя."""
    try:
        with open(path, 'r', encoding='utf-8') as file:
            data = json.load(file)
        return data
    except FileNotFoundError:
        print(f"Ошибка: Файл '{path}' не найден.")
    except json.JSONDecodeError:
        print("Ошибка: Файл содержит некорректный JSON.")
    except Exception as e:
        print(f"Неизвестная ошибка: {e}")
    
    return None

def get_genre_keyboard() -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Фантастика", callback_data="genre_Фантастика")],
        [InlineKeyboardButton(text="Детектив", callback_data="genre_Детектив")],
        [InlineKeyboardButton(text="Бизнес", callback_data="genre_Бизнес")],
        [InlineKeyboardButton(text="Любой жанр", callback_data="genre_any")]
    ])
    return keyboard
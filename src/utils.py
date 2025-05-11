import json
from typing import Optional, Dict

def load_intents_data(path='data/intents.json') -> Optional[Dict]:
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

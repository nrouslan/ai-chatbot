import json
import random
from typing import Optional, Dict, List

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

def get_random_response(intent_data: Dict[str, List[str]]) -> str:
    """Возвращает случайный ответ из поля 'responses' объекта намерения."""
    return random.choice(intent_data['responses'])

def get_random_failure_phrase(intents_data: Dict[str, List[str]]) -> str:
    """Возвращает случайную фразу из массива 'failure_phrases'."""
    return random.choice(intents_data['failure_phrases'])

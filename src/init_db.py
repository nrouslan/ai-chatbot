from typing import Dict
from utils import load_json_data
from constants import BOOK_ADS_PATH
from db import BookDatabase

def initialize_database(json_data: Dict, db_name: str = 'data/books.db') -> None:
    """
    Инициализирует базу данных с использованием класса BookDatabase.
    
    Args:
        json_data: Словарь с данными о книгах
        db_name: Имя файла базы данных (по умолчанию 'data/books.db')
    """
    # Создаем экземпляр класса BookDatabase
    db = BookDatabase(db_name)
    
    # Сохраняем данные в базу
    db.save_books_data(json_data['book_ads'])
    
    print(f"База данных успешно инициализирована в файле '{db_name}'")

    return db

# Пример использования
if __name__ == '__main__':
    # Загружаем данные из JSON
    book_ads_data = load_json_data(BOOK_ADS_PATH)
    
    # Инициализируем базу данных
    initialize_database(book_ads_data)

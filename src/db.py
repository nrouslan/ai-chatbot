import sqlite3
from typing import Dict, List

class BookDatabase:
    def __init__(self, db_name: str = 'data/books.db'):
        """
        Инициализирует подключение к базе данных.
        
        Args:
            db_name: Путь к файлу базы данных
        """
        self.db_name = db_name
        self._create_tables()

    def _create_tables(self) -> None:
        """Создает необходимые таблицы в базе данных"""
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            
            # Таблица жанров
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS genres (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL
            )
            ''')
            
            # Таблица книг
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS books (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                genre_id INTEGER NOT NULL,
                title TEXT NOT NULL,
                description TEXT,
                price TEXT,
                author TEXT,
                year INTEGER,
                rating REAL,
                pages INTEGER,
                isbn TEXT UNIQUE,
                cover TEXT,
                FOREIGN KEY (genre_id) REFERENCES genres(id)
            )
            ''')
            
            # Таблица похожих книг
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS similar_books (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                book_id INTEGER NOT NULL,
                title TEXT NOT NULL,
                FOREIGN KEY (book_id) REFERENCES books(id)
            )
            ''')
            
            # Таблица цитат
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS quotes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                book_id INTEGER NOT NULL,
                text TEXT NOT NULL,
                FOREIGN KEY (book_id) REFERENCES books(id)
            )
            ''')
            
            conn.commit()

    def save_books_data(self, book_ads: Dict[str, List[Dict]]) -> None:
        """
        Сохраняет данные о книгах в базу данных.
        
        Args:
            book_ads: Словарь с данными о книгах по жанрам
        """
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            
            # Очищаем существующие данные
            cursor.execute('DELETE FROM quotes')
            cursor.execute('DELETE FROM similar_books')
            cursor.execute('DELETE FROM books')
            cursor.execute('DELETE FROM genres')
            
            # Заполняем данными
            for genre_name, books in book_ads.items():
                # Добавляем жанр
                cursor.execute('INSERT INTO genres (name) VALUES (?)', (genre_name,))
                genre_id = cursor.lastrowid
                
                for book in books:
                    # Добавляем книгу
                    cursor.execute('''
                    INSERT INTO books (
                        genre_id, title, description, price, author, 
                        year, rating, pages, isbn, cover
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        genre_id, book['title'], book['description'], book['price'],
                        book['author'], book['year'], book['rating'], book['pages'],
                        book['isbn'], book['cover']
                    ))
                    book_id = cursor.lastrowid
                    
                    # Добавляем похожие книги
                    for similar_title in book.get('similar', []):
                        cursor.execute('''
                        INSERT INTO similar_books (book_id, title) VALUES (?, ?)
                        ''', (book_id, similar_title))
                    
                    # Добавляем цитаты
                    for quote in book.get('quotes', []):
                        cursor.execute('''
                        INSERT INTO quotes (book_id, text) VALUES (?, ?)
                        ''', (book_id, quote))
            
            conn.commit()

    def get_all_books_data(self) -> Dict[str, List[Dict]]:
        """
        Получает все данные о книгах из базы данных.
        
        Returns:
            Словарь с данными о книгах в формате, аналогичном исходному JSON
        """
        with sqlite3.connect(self.db_name) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # Получаем все жанры
            cursor.execute('SELECT id, name FROM genres')
            genres = {row['id']: row['name'] for row in cursor.fetchall()}
            
            result = {}
            
            for genre_id, genre_name in genres.items():
                cursor.execute('SELECT * FROM books WHERE genre_id = ?', (genre_id,))
                books = []
                
                for book_row in cursor.fetchall():
                    book_id = book_row['id']
                    
                    # Получаем похожие книги
                    cursor.execute('SELECT title FROM similar_books WHERE book_id = ?', (book_id,))
                    similar = [row['title'] for row in cursor.fetchall()]
                    
                    # Получаем цитаты
                    cursor.execute('SELECT text FROM quotes WHERE book_id = ?', (book_id,))
                    quotes = [row['text'] for row in cursor.fetchall()]
                    
                    books.append({
                        'title': book_row['title'],
                        'description': book_row['description'],
                        'price': book_row['price'],
                        'author': book_row['author'],
                        'year': book_row['year'],
                        'rating': book_row['rating'],
                        'pages': book_row['pages'],
                        'isbn': book_row['isbn'],
                        'cover': book_row['cover'],
                        'similar': similar,
                        'quotes': quotes
                    })
                
                result[genre_name] = books
            
            return {'book_ads': result}

    # def get_book_details(self, title: str) -> str:
    #     """Возвращает подробную информацию о книге по её названию"""
    #     book_ads = self.get_all_books_data()['book_ads']
        
    #     for genre, books in book_ads.items():
    #         for book in books:
    #             if book.get("title", "").lower() == title.lower():
    #                 details = (
    #                     f"📚 <b>{book['title']}</b>\n"
    #                     f"Автор: {book.get('author', 'Неизвестно')}\n"
    #                     f"Год издания: {book.get('year', '—')}\n"
    #                     f"Рейтинг: {book.get('rating', '—')}/5\n"
    #                     f"Страниц: {book.get('pages', '—')}\n"
    #                     f"ISBN: {book.get('isbn', '—')}\n"
    #                     f"Цена: {book.get('price', '—')}\n"
    #                     f"Описание: {book.get('description', '—')}\n"
    #                 )

    #                 # Добавим цитату, если есть
    #                 if book.get("quotes"):
    #                     details += f"\n💬 Цитата: «{book['quotes'][0]}»"

    #                 # Похожие книги
    #                 if book.get("similar"):
    #                     details += f"\n📖 Похожие книги: {', '.join(book['similar'])}"

    #                 return details

    #     return "Книга не найдена. Убедитесь, что название указано точно."

    # def search_books(self, query: str, limit: int = 5) -> List[Dict]:
    #     """Поиск книг по названию или автору"""
    #     with sqlite3.connect(self.db_name) as conn:
    #         conn.row_factory = sqlite3.Row
    #         cursor = conn.cursor()
            
    #         search_query = f"%{query.lower()}%"
            
    #         cursor.execute('''
    #         SELECT b.*, g.name as genre 
    #         FROM books b
    #         JOIN genres g ON b.genre_id = g.id
    #         WHERE LOWER(b.title) LIKE ? OR LOWER(b.author) LIKE ?
    #         LIMIT ?
    #         ''', (search_query, search_query, limit))
            
    #         results = []
    #         for row in cursor.fetchall():
    #             book_id = row['id']
                
    #             # Получаем похожие книги
    #             cursor.execute('SELECT title FROM similar_books WHERE book_id = ?', (book_id,))
    #             similar = [r['title'] for r in cursor.fetchall()]
                
    #             # Получаем цитаты
    #             cursor.execute('SELECT text FROM quotes WHERE book_id = ?', (book_id,))
    #             quotes = [r['text'] for r in cursor.fetchall()]
                
    #             results.append({
    #                 'title': row['title'],
    #                 'author': row['author'],
    #                 'genre': row['genre'],
    #                 'year': row['year'],
    #                 'rating': row['rating'],
    #                 'similar': similar,
    #                 'quotes': quotes
    #             })
            
    #         return results

    # def get_books_by_genre(self, genre_name: str) -> List[Dict]:
        """Получает все книги указанного жанра"""
        book_ads = self.get_all_books_data()['book_ads']
        return book_ads.get(genre_name, [])
from ads.constants import ADS

def get_book_recommendations(genre=None):
    if genre and genre in ADS['book_ads']:
        books = ADS['book_ads'][genre]
    else:
        books = []
        for genre_books in ADS['book_ads'].values():
            books.extend(genre_books)
    
    if not books:
        return "К сожалению, сейчас нет рекомендаций."
    
    response = "Вот несколько отличных книг:\n\n"
    for book in books[:3]:  # Ограничиваем 3 книгами
        response += f"📖 <b>{book['title']}</b>\n"
        response += f"   {book['description']}\n"
        response += f"   Цена: {book['price']}\n\n"
    
    response += "Хотите узнать больше о какой-то из них?"
    return response

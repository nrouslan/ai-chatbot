from telegram import InlineKeyboardButton, InlineKeyboardMarkup

def create_book_keyboard():
    keyboard = [
        [InlineKeyboardButton("Фантастика", callback_data='genre_Фантастика')],
        [InlineKeyboardButton("Детектив", callback_data='genre_Детектив')],
        [InlineKeyboardButton("Бизнес", callback_data='genre_Бизнес')],
        [InlineKeyboardButton("Любой жанр", callback_data='genre_any')]
    ]
    return InlineKeyboardMarkup(keyboard)
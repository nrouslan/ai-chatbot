from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext

from bot import get_response_by_message_text

async def start_command_handler(update: Update, _: CallbackContext) -> None:
    await update.message.reply_text(
        'Привет! Я книжный бот. Я могу порекомендовать вам интересные книги. '
        'Просто напишите "Посоветуй книгу" или выберите жанр:',
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("Фантастика", callback_data='genre_fantasy')],
            [InlineKeyboardButton("Детектив", callback_data='genre_detective')],
            [InlineKeyboardButton("Бизнес", callback_data='genre_business')],
            [InlineKeyboardButton("Любой жанр", callback_data='genre_any')]
        ])
    )

async def help_command_handler(update: Update, _: CallbackContext) -> None:
    await update.message.reply_text(
        "Я могу:\n"
        "- Рекомендовать книги (просто напишите 'Посоветуй книгу')\n"
        "- Рассказать о конкретных книгах\n"
        "- Принимать голосовые сообщения\n"
        "- Помочь выбрать книгу по жанру\n\n"
    )
    
async def message_text_handler(update: Update, context: CallbackContext) -> None:        
    await update.message.reply_text(get_response_by_message_text(
        update.message.text, context.bot_data['pipeline'], context.bot_data['intents_data']))

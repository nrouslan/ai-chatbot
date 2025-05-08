from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext

from utils import get_random_response, get_random_failure_phrase

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
    text_preprocessor = context.bot_data['text_preprocessor']
    pipeline = context.bot_data['pipeline']
    intents_data = context.bot_data['intents_data']
    
    cleaned = text_preprocessor.preprocess(update.message.text)
    intent = pipeline.predict([cleaned])[0]

    response = ''
    if (intent in intents_data['intents']):
        response = get_random_response(intents_data['intents'][intent])
    else:
        response = get_random_failure_phrase(intents_data)
    await update.message.reply_text(response)

# TODO: Добавить логи классификации намерений в консоль...
# TODO: Как сделать так, чтобы модель все-таки не классифицировала намерение, которое не знает...
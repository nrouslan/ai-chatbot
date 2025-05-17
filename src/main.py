import os

from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters
from dotenv import load_dotenv

from handlers import start_command_handler, help_command_handler, \
    message_text_handler, voice_message_handler

from ml import get_intents_data_and_targets, train_intents_classifier
from nlp import TextPreprocessor
from utils import load_intents_data
from constants import VOICE_DIR

if __name__ == '__main__':
    # Подготовка папки для хранения голосовых сообщений.
    if not os.path.exists(VOICE_DIR):
        os.makedirs(VOICE_DIR)
        
    # Загрузка переменных из .env в окружение.
    load_dotenv()

    intents_data = load_intents_data()
    X_train, y_train = get_intents_data_and_targets(intents_data)
    
    text_preprocessor = TextPreprocessor()
    pipeline = train_intents_classifier([text_preprocessor.preprocess(text) for text in X_train], y_train)

    app = ApplicationBuilder().token(os.getenv("API_KEY")).build()
    
    app.bot_data['intents_data'] = intents_data
    app.bot_data['pipeline'] = pipeline
    app.bot_data['session_state'] = { 'last_intent': '' }

    app.add_handler(CommandHandler("start", start_command_handler))
    app.add_handler(CommandHandler("help", help_command_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_text_handler))
    app.add_handler(MessageHandler(filters.VOICE, voice_message_handler))

    print("--> Telegram-бот запущен! Ссылка на бота: https://t.me/bookseller1111_bot")

    app.run_polling()

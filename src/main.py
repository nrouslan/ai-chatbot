"""Телеграм бот для продажи книг"""

import os

from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, CallbackQueryHandler, filters

from sklearn.svm import LinearSVC
from sklearn.feature_extraction.text import TfidfVectorizer

from bot.handlers import start_command, help_command, handle_text_message, handle_voice_message, button_handler

from nlp.constants import BOT_CONFIG
from bot.constants import BOT_API_KEY, VOICE_DIR

from prepare_data import prepare_data

def main():
    if not os.path.exists(VOICE_DIR):
        os.makedirs(VOICE_DIR)
        
    print("--> Обучение классификатора намерений...")

    X_text = []  # ['Хэй', 'хаюхай', 'Хаюшки', ...]
    y = []  # ['hello', 'hello', 'hello', ...]

    for intent, intent_data in BOT_CONFIG['intents'].items():
        for example in intent_data['examples']:
            X_text.append(example)
            y.append(intent)

    vectorizer = TfidfVectorizer(analyzer='char', ngram_range=(3, 3))
    X = vectorizer.fit_transform(X_text)
    classifier = LinearSVC()
    classifier.fit(X, y)

    dialogues = prepare_data()

    print("--> Запуск Telegram-бота...")

    app = ApplicationBuilder().token(BOT_API_KEY).build()
    
    stats = {'intent': 0, 'generate': 0, 'failure': 0}
    
    app.bot_data['stats'] = stats
    app.bot_data['dialogues'] = dialogues
    app.bot_data['classifier'] = classifier
    app.bot_data['vectorizer'] = vectorizer
    app.bot_data['theme_history'] = []
    
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text_message))
    app.add_handler(MessageHandler(filters.VOICE, handle_voice_message))
    app.add_handler(CallbackQueryHandler(button_handler))

    print("--> Telegram-бот запущен! Ссылка на бота: https://t.me/bookseller1111_bot")
    app.run_polling()

if __name__ == '__main__':
    main()
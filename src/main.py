"""Телеграм бот для продажи книг"""

import os

from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, CallbackQueryHandler, filters

from sklearn.svm import LinearSVC
from sklearn.feature_extraction.text import TfidfVectorizer

from nlp.utils import clear_phrase
from bot.handlers import start_command, help_command, handle_text_message, handle_voice_message, button_handler

from nlp.constants import BOT_CONFIG
from bot.constants import BOT_API_KEY, VOICE_DIR

if not os.path.exists(VOICE_DIR):
    os.makedirs(VOICE_DIR)

"""Обучение классификатора намерений"""
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


"""Подготовка данных из датасета dialogues.txt"""
print("--> Подготовка данных из датасета dialogues.txt...")


with open('dialogues.txt', 'r', encoding='utf-8') as f:
    content = f.read()

# Разбиваем на пары по признаку двойного перевода строки
dialogues_str = content.split('\n\n')
dialogues = [dialogue_str.split('\n')[:2] for dialogue_str in dialogues_str]

dialogues_filtered = []
questions = set()

# Убираем все после второй строки
for dialogue in dialogues:
    if len(dialogue) != 2:
        continue
    
    question, answer = dialogue
    question = clear_phrase(question[2:])
    answer = answer[2:]
   
    if question != '' and question not in questions:
        questions.add(question)
        dialogues_filtered.append([question, answer])

dialogues_structured = {}  #  {'word': [['...word...', 'answer'], ...], ...}

# Формируем структурированные диалоги
# Формат: replica -> word1, word2, word3, ... -> dialogues_structured[word1] + dialogues_structured[word2] + ... -> mini_dataset

for question, answer in dialogues_filtered:
    words = set(question.split(' '))
    for word in words:
        if word not in dialogues_structured:
            dialogues_structured[word] = []
        dialogues_structured[word].append([question, answer])

dialogues_structured_cut = {}
for word, pairs in dialogues_structured.items():
    pairs.sort(key=lambda pair: len(pair[0]))
    dialogues_structured_cut[word] = pairs[:1000]


def main():
    print("--> Запуск Telegram-бота...")

    app = ApplicationBuilder().token(BOT_API_KEY).build()
    
    stats = {'intent': 0, 'generate': 0, 'failure': 0}
    
    app.bot_data['stats'] = stats
    app.bot_data['dialogues'] = dialogues_structured_cut
    app.bot_data['classifier'] = classifier
    app.bot_data['vectorizer'] = vectorizer
    
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text_message))
    app.add_handler(MessageHandler(filters.VOICE, handle_voice_message))
    app.add_handler(CallbackQueryHandler(button_handler))

    print("--> Telegram-бот запущен! Ссылка на бота: https://t.me/bookseller1111_bot")
    app.run_polling()

if __name__ == '__main__':
    main()
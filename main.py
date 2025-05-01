"""Телеграм бот для продажи книг"""

from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, CallbackContext

from sklearn.svm import LinearSVC
from sklearn.feature_extraction.text import TfidfVectorizer

from utils.clear_phrase import clear_phrase
from nlp.get_answer import get_answer

from constants import BOT_CONFIG, BOT_API_KEY

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

"""Тестирование нейронной сети"""

stats = {'intent': 0, 'generate': 0, 'failure': 0}

# question = None
# hist_theme = []

# while (True):
#     question = input('> ')
#     if question != '':
#         answer = get_answer(question, stats, dialogues_structured_cut, classifier, vectorizer)
#         if answer is not None:
#             print('< ' + answer)
#             print(stats)
#             # print(hist_theme)
#     else:
#         break
    
"""Telegram API"""

async def start_command(update: Update, _: CallbackContext) -> None:
    """Отправка стартового сообщения."""
    await  update.message.reply_text('Привет!')

async def help_command(update: Update, _: CallbackContext) -> None:
    """Отправка справки по боту."""
    await update.message.reply_text('Это справка по боту...')

async def handle_user_message(update: Update, _: CallbackContext) -> None:
    """Обработка реплики."""
    replica = update.message.text
    answer = get_answer(replica, stats, dialogues_structured_cut, classifier, vectorizer)
    
    await update.message.reply_text(answer)
   
    print(f"--> stats: {stats}")
    print(f"--> replica: {replica}")
    print(f"--> answer: {answer}\n")

def main():
    """Запуск Telegram-бота."""
    print("--> Запуск Telegram-бота...")

    # Создаём бота
    app = ApplicationBuilder().token(BOT_API_KEY).build()
    
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_user_message))

    print("--> Telegram-бот запущен! Ссылка на бота: https://t.me/bookseller1111_bot")
    # Запуск бота
    app.run_polling()

main()

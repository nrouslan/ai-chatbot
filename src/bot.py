import random
from nlp import TextPreprocessor, is_similar
from nltk import edit_distance
from sklearn.pipeline import Pipeline
from typing import Dict, List, Any, Union, Optional
from dialogues import Dialogues
from constants import THEME_HISTORY_LENGTH

def get_response_by_message_text(
    message_text: str, 
    pipeline: Pipeline, 
    intents_data: Dict[str, dict],
    dialogues: Dialogues,
    theme_history: List[str],
    book_ads: Dict[str, list]
) -> str:
    """Возвращает ответ на сообщение пользователя."""

    intent = classify_intent(
        message_text,
        pipeline,
        intents_data['intents'],
        theme_history
    )

    if intent:
        responses = intents_data['intents'].get(intent, {}).get('responses')
        if responses:
            return get_random_response(responses)
    
    book_result = handle_book_query(book_ads, message_text)
    if (book_result):
        return book_result

    return generate_answer(message_text, dialogues) or get_random_failure_phrase(intents_data['failure_phrases'])

def classify_intent(
    message_text: str, 
    pipeline: Pipeline, 
    intents: Dict, 
    theme_history
) -> str:
    """Определяет намерение пользователя на основе текста сообщения и истории тем."""

    for i, theme in enumerate(theme_history):
        intent = classify_intent_by_theme(message_text, pipeline, intents, theme)
        if intent:
            if i > 0:
                theme_history[:] = theme_history[i:]
            break
    else:
        # Если ни одна тема не сработала, пробуем без темы
        intent = classify_intent_by_theme(message_text, pipeline, intents)

    if intent:
        # Обновляем историю, если интент определён и у него есть тема
        theme = intents[intent].get('theme_gen')
        if theme and theme not in theme_history:
            theme_history.insert(0, theme)
            if len(theme_history) > THEME_HISTORY_LENGTH:
                theme_history.pop()
    else:
        # Если интент не определён — очищаем историю тем
        theme_history.clear()

    return intent

def handle_book_query(book_ads: Dict[str, List[Dict]], message_text: str) -> str:
    """Обрабатывает пользовательский ввод и возвращает подробности о книге, если найдена похожая."""
    
    text_preprocessor = TextPreprocessor()
    cleaned_text = text_preprocessor.clear_phrase(message_text)
    candidates = []

    # Защита от бессмысленного ввода
    if len(cleaned_text) < 4:
        return None

    for genre_books in book_ads.values():
        for book in genre_books:
            title = book.get("title", "")
            cleaned_title = text_preprocessor.clear_phrase(title)

            # Подстрочное совпадение — при достаточной длине
            if len(cleaned_text) >= 5 and cleaned_text in cleaned_title:
                candidates.append((0.0, title))
                continue

            # Расчет расстояния Левенштейна
            if abs(len(cleaned_text) - len(cleaned_title)) / max(len(cleaned_title), 1) < 0.3:
                dist = edit_distance(cleaned_text, cleaned_title)
                score = dist / max(len(cleaned_title), 1)

                if score < 0.3:  # допустимый уровень "похожести"
                    candidates.append((score, title))

    if not candidates:
        return None

    best_match = sorted(candidates, key=lambda x: x[0])[0]
    if best_match[0] > 0.25:  # даже лучший кандидат недостаточно близок
        return "Не удалось точно определить книгу. Попробуйте переформулировать запрос."

    return get_book_details(book_ads, best_match[1])
    
def classify_intent_by_theme(message_text: str, pipeline: Pipeline, intents: Dict, theme=None):
    """Функция для классификации намерения по теме."""

    text_preprocessor = TextPreprocessor()
    cleaned_text = text_preprocessor.clear_phrase(message_text)

    def is_theme_match(theme_app):
        return (
            theme_app is None and theme is None or
            theme_app and (theme in theme_app or '*' in theme_app)
        )
    
    def is_similar_to_examples(intent_data):
        return any(
            is_similar(cleaned_text, text_preprocessor.clear_phrase(example))
            for example in intent_data.get('examples', [])
        )

    # 1. Проверка предсказанного интента
    predicted_intent = pipeline.predict([cleaned_text])[0]
    intent_data = intents.get(predicted_intent)
    if intent_data and is_theme_match(intent_data.get('theme_app')) and is_similar_to_examples(intent_data):
        return predicted_intent

    # 2. Эвристическая проверка по другим интентам
    for intent, intent_data in intents.items():
        if is_theme_match(intent_data.get('theme_app')) and is_similar_to_examples(intent_data):
            return intent

    return None

def generate_answer(message_text: str, dialogues: Dialogues) -> Union[Any, None]:
    """Генерация ответа на основе похожих вопросов из диалогов."""

    text_preprocessor = TextPreprocessor()
    cleaned_text = text_preprocessor.clear_phrase(message_text)
    words = set(cleaned_text.split())

    # Собираем релевантные пары (вопрос, ответ), исключая повторы
    mini_dataset = {
        tuple(pair) for word in words if word in dialogues for pair in dialogues[word]
    }

    candidates = []
    for question, answer in mini_dataset:
        if abs(len(cleaned_text) - len(question)) / len(question) < 0.2:
            distance = edit_distance(cleaned_text, question)
            distance_weighted = distance / len(question)
            if distance_weighted < 0.2:
                candidates.append((distance_weighted, question, answer))

    return min(candidates, key=lambda x: x[0])[2] if candidates else None

def get_random_response(responses: List[str]) -> str:
    """Возвращает случайный ответ из поля 'responses' объекта намерения."""
    return random.choice(responses)

def get_random_failure_phrase(failure_phrases: List[str]) -> str:
    """Возвращает случайную фразу из массива 'failure_phrases'."""
    return random.choice(failure_phrases)

def get_book_recommendations(book_ads: Dict, genre: Optional[str] = None) -> str:
    """Возвращает рекомендации книг по жанру или случайному жанру, если жанр не указан."""

    if not genre or genre not in book_ads:
        available_genres = list(book_ads.keys())
        if not available_genres:
            return "К сожалению, сейчас нет рекомендаций."
        genre = random.choice(available_genres)

    books = book_ads.get(genre, [])
    if not books:
        return "К сожалению, сейчас нет рекомендаций."

    response = "Вот несколько отличных книг:\n\n"
    for book in books[:3]:
        response += (
            f"📖 <b>{book['title']}</b>\n"
            f"   {book['description']}\n"
            f"   Цена: {book['price']}\n\n"
        )
    response += "Хотите узнать больше о какой-то из них?"
    return response

def get_book_details(book_ads: Dict[str, list], title: str) -> str:
    """Возвращает подробную информацию о книге по её названию."""

    for genre, books in book_ads.items():
        for book in books:
            if book.get("title", "").lower() == title.lower():
                details = (
                    f"📚 <b>{book['title']}</b>\n"
                    f"Автор: {book.get('author', 'Неизвестно')}\n"
                    f"Год издания: {book.get('year', '—')}\n"
                    f"Рейтинг: {book.get('rating', '—')}/5\n"
                    f"Страниц: {book.get('pages', '—')}\n"
                    f"ISBN: {book.get('isbn', '—')}\n"
                    f"Цена: {book.get('price', '—')}\n"
                    f"Описание: {book.get('description', '—')}\n"
                )

                # Добавим цитату, если есть
                if book.get("quotes"):
                    details += f"\n💬 Цитата: «{book['quotes'][0]}»"

                # Похожие книги
                if book.get("similar"):
                    details += f"\n📖 Похожие книги: {', '.join(book['similar'])}"

                return details

    return "Книга не найдена. Убедитесь, что название указано точно."

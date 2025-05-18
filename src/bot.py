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
    theme_history: List[str]
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

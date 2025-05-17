import random
from nlp import TextPreprocessor, is_similar
from nltk import edit_distance
from sklearn.pipeline import Pipeline
from typing import Dict, List, Any, Union
from dialogues import Dialogues

def get_response_by_message_text(
    message_text: str, 
    pipeline: Pipeline, 
    intents_data: Dict[str, dict],
    session_state: Dict[str, str],
    dialogues: Dialogues
) -> str:
    """Функция для получения ответа на сообщение пользователя."""

    intents = intents_data['intents']
    text_preprocessor = TextPreprocessor()
    current_intent = session_state.get("last_intent")

    # Предсказание намерения пользователя.
    message_text_cleaned = text_preprocessor.preprocess(message_text)
    predicted_intent = pipeline.predict([message_text_cleaned])[0]
        
    # Проверка, подходит ли к текущему контексту.
    if current_intent:
        allowed_next = intents.get(current_intent, {}).get("next_intents", [])
        if predicted_intent not in allowed_next:
            predicted_intent = current_intent # Останемся в текущем контексте.

    # Поиск похожего примера.
    if predicted_intent in intents:
        for example in intents[predicted_intent]['examples']:
            example_cleaned = text_preprocessor.preprocess(example)
            if is_similar(message_text_cleaned, example_cleaned):
                session_state["last_intent"] = predicted_intent
                return get_random_response(intents[predicted_intent]['responses'])
            
    # Если пример не найден для интента, генерируем ответ
    answer = generate_answer(message_text_cleaned, dialogues)
    if answer:
        return answer

    return get_random_failure_phrase(intents_data['failure_phrases'])

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

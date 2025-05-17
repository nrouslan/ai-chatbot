import random
from nlp import TextPreprocessor, is_similar
from sklearn.pipeline import Pipeline
from typing import List, Dict

def get_response_by_message_text(
    message_text: str, 
    pipeline: Pipeline, 
    intents_data: Dict[str, dict],
    session_state: Dict[str, str]
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

    return get_random_failure_phrase(intents_data['failure_phrases'])

def get_random_response(responses: List[str]) -> str:
    """Возвращает случайный ответ из поля 'responses' объекта намерения."""
    return random.choice(responses)

def get_random_failure_phrase(failure_phrases: List[str]) -> str:
    """Возвращает случайную фразу из массива 'failure_phrases'."""
    return random.choice(failure_phrases)

import random
from nlp import TextPreprocessor, is_similar
from sklearn.pipeline import Pipeline
from typing import List, Dict

def get_response_by_message_text(message_text: str, pipeline: Pipeline, intents_data: Dict[str, dict]):
    """Функция для получения ответа на сообщение пользователя."""
    text_preprocessor = TextPreprocessor()
    
    # Предсказание намерения пользователя.
    message_text_cleaned = text_preprocessor.preprocess(message_text)
    intent = pipeline.predict([message_text_cleaned])[0]

    # Возврат подходящего ответа.
    intents = intents_data['intents']    
    if intent in intents:
        for example in intents[intent]['examples']:
            example_cleaned = text_preprocessor.preprocess(example)
            if is_similar(message_text_cleaned, example_cleaned):
                return get_random_response(intents[intent]['responses'])

    return get_random_failure_phrase(intents_data['failure_phrases'])

def get_random_response(responses: List[str]) -> str:
    """Возвращает случайный ответ из поля 'responses' объекта намерения."""
    return random.choice(responses)

def get_random_failure_phrase(failure_phrases: List[str]) -> str:
    """Возвращает случайную фразу из массива 'failure_phrases'."""
    return random.choice(failure_phrases)

import random

from nltk import edit_distance

from nlp.constants import BOT_CONFIG
from nlp.classification import classify_intent
from nlp.utils import clear_phrase

def get_answer(replica, stats, dialogues_dataset, classifier, vectorizer):
    """Основная функция бота - по фразе (replica) выдать ответ."""

    # Проверяем намерения
    intent = classify_intent(replica, classifier, vectorizer)

    # Выбор заготовленной реплики
    if intent:
        answer = get_answer_by_intent(intent)
        if answer:
            stats['intent'] += 1
            return answer

    # Вызов генеративной модели
    answer = generate_answer(replica, dialogues_dataset)
    if answer:
        stats['generate'] += 1
        return answer
   
    # Если не понятно намерение – выдаем стандартную фразу
    stats['failure'] += 1
    return get_failure_phrase()


def get_answer_by_intent(intent):
    """Выдает случайные ответ по известному намерению из словаря намерений."""

    if intent in BOT_CONFIG['intents']:
        responses = BOT_CONFIG['intents'][intent]['responses']
        return random.choice(responses)


def generate_answer(replica, dialogues_dataset):
    """Функция генерации ответа."""

    replica = clear_phrase(replica)
    words = set(replica.split(' '))

    mini_dataset = []
    for word in words:
        if word in dialogues_dataset:
            mini_dataset += dialogues_dataset[word]
            
    # TODO убрать повторы из mini_dataset!

    answers = []  # [[distance_weighted, question, answer]]

    for question, answer in mini_dataset:
        # Проверка на схожесть длины реплики и вопроса
        if abs(len(replica) - len(question)) / len(question) < 0.2:
            # Вычисление взвешенного расстояния Левенштейна
            distance = edit_distance(replica, question)
            distance_weighted = distance / len(question)
            if distance_weighted < 0.2:
                answers.append([distance_weighted, question, answer])
   
    if answers:
        return min(answers, key=lambda three: three[0])[2]


def get_failure_phrase():
    """Выдать случайную фразу на неизвестное намерение."""
    failure_phrases = BOT_CONFIG['failure_phrases']
    return random.choice(failure_phrases)

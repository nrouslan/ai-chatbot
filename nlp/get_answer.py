from nlp.classify_intent import classify_intent
from nlp.get_answer_by_intent import get_answer_by_intent
from nlp.generate_answer import generate_answer
from nlp.get_failure_phrase import get_failure_phrase

def get_answer(replica, stats, dialogues_dataset, classifier, vectorizer):
    """Основная функция бота - по фразе (replica) выдать ответ."""
    intent = classify_intent(replica, classifier, vectorizer) # Проверяем намерения

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

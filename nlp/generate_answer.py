from nltk import edit_distance
from utils.clear_phrase import clear_phrase

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

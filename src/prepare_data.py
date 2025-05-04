"""Подготовка данных из датасета dialogues.txt"""

from nlp.utils import clear_phrase

def prepare_data():
    print('--> Подготовка данных из датасета dialogues.txt...')
    
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
        question = clear_phrase(question[2:], spell_check=False)
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
        
    return dialogues_structured_cut

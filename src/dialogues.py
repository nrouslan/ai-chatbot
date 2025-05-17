"""Подготовка данных из датасета dialogues.txt"""

from nlp import TextPreprocessor
from typing import Dict, List, Any
from typing_extensions import TypeAlias

from constants import DIALOGUES_DATASET_PATH

Dialogues: TypeAlias = Dict[Any, List]

def prepare_dialogues() -> Dialogues:
    textPreprocessor = TextPreprocessor()
    
    print('--> Подготовка данных из датасета dialogues.txt...')

    with open(DIALOGUES_DATASET_PATH, 'r', encoding='utf-8') as f:
        dialogues = [d.split('\n')[:2] for d in f.read().split('\n\n')]

    dialogues_filtered = []
    seen_questions = set()

    for pair in dialogues:
        if len(pair) != 2:
            continue

        question = textPreprocessor.clear_phrase(pair[0][2:])
        answer = pair[1][2:]

        if question and question not in seen_questions:
            seen_questions.add(question)
            dialogues_filtered.append([question, answer])

    dialogues_structured = {}

    for question, answer in dialogues_filtered:
        for word in set(question.split()):
            dialogues_structured.setdefault(word, []).append([question, answer])

    # Ограничим по 1000 записей на слово
    result = {
        word: sorted(pairs, key=lambda p: len(p[0]))[:1000]
        for word, pairs in dialogues_structured.items()
    }
    
    print('--> Подготовка данных завершена.')
    
    return result

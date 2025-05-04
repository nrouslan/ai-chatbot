import re
from nltk import edit_distance

from nlp.constants import SPELL_CORRECTION_DICT

def clear_phrase(phrase, spell_check=True):
    """Функция очистки фраз от «мусора»."""

    # 1. Приведение к нижнему регистру
    phrase = phrase.lower()

    # 2. Удаление специальных символов (кроме букв, цифр, дефисов и пробелов)
    phrase = re.sub(r'[^а-яё0-9\s-]', '', phrase)
    
    # 3. Замена множественных пробелов и дефисов на одинарные
    phrase = re.sub(r'[\s-]+', ' ', phrase).strip()
    
    # 4. Коррекция опечаток
    if (spell_check):
        corrected_words = []
        for word in phrase.split():
            # Проверка словаря быстрых замен
            if word in SPELL_CORRECTION_DICT:
                corrected_words.append(SPELL_CORRECTION_DICT[word])
                continue
                
            # Поиск ближайшего слова по Левенштейну
            closest_word = None
            min_distance = float('inf')
            
            for correct_word in SPELL_CORRECTION_DICT.values():
                dist = edit_distance(word, correct_word)
                if dist < min_distance and dist <= 2:
                    min_distance = dist
                    closest_word = correct_word
            
            corrected_words.append(closest_word if closest_word else word)
        
        phrase = ' '.join(corrected_words)

    return phrase

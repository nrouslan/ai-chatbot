from nltk import edit_distance

from nlp.utils import clear_phrase
from nlp.constants import BOT_CONFIG, THEME_HISTORY_LENGTH

def classify_intent(replica, classifier, vectorizer, theme_history):
    lev = 0
    intent = None
        
    # Перебор истории тем
    for theme in theme_history:
        intent = classify_intent_by_theme(replica, classifier, vectorizer, theme)
        if intent is not None:
            break
        lev += 1

    if intent is None:  # Если по темам не обнаружено намерений, то ищем без темы
        lev = 0  # Чтобы не очистить историю тем (можно и как вариант очищать, чтобы при непонятных ситуациях забывать историю)
        intent = classify_intent_by_theme(replica, classifier, vectorizer)
    else:
        if lev > 0:
            theme_history = theme_history[lev:]  # Перескок на более старую тему, если определили её

    if intent is not None:
        if 'theme_gen' in BOT_CONFIG['intents'][intent]:  # Если намерение генерирует новую тему
            if BOT_CONFIG['intents'][intent]['theme_gen'] not in theme_history:  # И её ещё нет в истории
                theme_history.insert(0, BOT_CONFIG['intents'][intent]['theme_gen'])  # То добавляем в историю тему
                if (len(theme_history) > THEME_HISTORY_LENGTH):
                    theme_history.pop()  # Ограничение длины истории тем

    return intent


def classify_intent_by_theme(replica, classifier, vectorizer, theme=None):
    replica = clear_phrase(replica)
    
    # intent = classifier.predict(vectorizer.transform([replica]))[0]

    for intent, intent_data in BOT_CONFIG['intents'].items():
        theme_app = None
        if 'theme_app' in intent_data:
            theme_app = intent_data['theme_app']

        if (theme_app is not None and (theme in theme_app or '*' in theme_app)) or (theme is None and theme_app is None):
            for example in intent_data['examples']:
                example = clear_phrase(example)

                distance = edit_distance(replica, example)
                if example and distance / len(example) <= 0.5:
                    return intent

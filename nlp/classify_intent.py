from nltk import edit_distance

from utils.clear_phrase import clear_phrase

from constants import BOT_CONFIG

# hist_theme = []

def classify_intent(replica, classifier, vectorizer):
    replica = clear_phrase(replica)

    intent = classifier.predict(vectorizer.transform([replica]))[0]
   
    for example in BOT_CONFIG['intents'][intent]['examples']:
        example = clear_phrase(example)
        distance = edit_distance(replica, example)
        if example and distance / len(example) <= 0.5:
            return intent

# def classify_intent(replica):
#     global hist_theme
#     lev = 0
#     intent = None

#     # Перебор истории тем
#     for theme in hist_theme:
#         intent = classify_intent_by_theme(replica, theme)
#         if intent is not None:
#             break
#         lev += 1

#     if intent is None:  # Если по темам не обнаружено намерений, то ищем без темы
#         lev = 0  # Чтобы не очистить историю тем (можно и как вариант очищать, чтобы при непонятных ситуациях забывать историю)
#         intent = classify_intent_by_theme(replica)
#     else:
#         if lev > 0:
#             hist_theme = hist_theme[lev:]  # Перескок на более старую тему, если определеили её

#     if intent is not None:
#         if 'theme_gen' in BOT_CONFIG['intents'][intent]:  # Если намерение генерирует новую тему
#             if BOT_CONFIG['intents'][intent]['theme_gen'] not in hist_theme:  # И её нет ещё в истории
#                 hist_theme.insert(0, BOT_CONFIG['intents'][intent]['theme_gen'])  # То добавляем в историю тему
#                 if (len(hist_theme) > HIST_THEME_LEN):
#                     hist_theme.pop()  # Ограничение длины истории тем
#     return intent

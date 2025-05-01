# from nltk import edit_distance

# from utils.clear_phrase import clear_phrase
# from constants import BOT_CONFIG

# # TODO: Добавить ML
# def classify_intent_by_theme(replica, theme=None):
#     replica = clear_phrase(replica)

#     for intent, intent_data in BOT_CONFIG['intents'].items():
#         theme_app = None
#         if 'theme_app' in intent_data:
#             theme_app = intent_data['theme_app']

#         if (theme_app is not None and (theme in theme_app or '*' in theme_app)) or ( theme is None and theme_app is None):
#             for example in intent_data['examples']:
#                 example = clear_phrase(example)

#                 distance = edit_distance(replica, example)
#                 if distance / len(example) < 0.4:
#                     return intent

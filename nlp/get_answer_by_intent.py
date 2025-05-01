import random
from constants import BOT_CONFIG

def get_answer_by_intent(intent):
    """Выдает случайные ответ по известному намерению из словаря намерений."""

    if intent in BOT_CONFIG['intents']:
        responses = BOT_CONFIG['intents'][intent]['responses']
        return random.choice(responses)

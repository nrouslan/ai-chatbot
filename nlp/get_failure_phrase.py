import random
from constants import BOT_CONFIG

def get_failure_phrase():
    """Выдать случайную фразу на неизвестное намерение."""
    failure_phrases = BOT_CONFIG['failure_phrases']
    return random.choice(failure_phrases)

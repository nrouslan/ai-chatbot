from nltk import edit_distance

from nlp.utils import clear_phrase
from nlp.constants import BOT_CONFIG

def classify_intent(replica, classifier, vectorizer):
    replica = clear_phrase(replica)

    intent = classifier.predict(vectorizer.transform([replica]))[0]
   
    for example in BOT_CONFIG['intents'][intent]['examples']:
        example = clear_phrase(example)
        distance = edit_distance(replica, example)
        if example and distance / len(example) <= 0.5:
            return intent

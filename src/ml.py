from typing import Dict, List, Tuple, Union

from sklearn.feature_extraction.text import CountVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline

def get_intents_data_and_targets(intents_data: Dict[str, dict]) -> Tuple[List[str], List[str]]:
    """Получение тренировочных данных и меток о намерениях пользователя."""
    X = []  # Список фраз
    y = []  # Список меток намерений

    for intent, intent_data in intents_data['intents'].items():
        examples = intent_data['examples']
        for example in examples:
            X.append(example)
            y.append(intent)
        
    return X, y

def train_intents_classifier(
    X_train: List[str],
    y_train: Union[List[str], List[int]]
) -> Pipeline:
    """Обучение классификатора намерений."""
    pipeline = Pipeline([
        ('vect', CountVectorizer()),
        ('clf', LogisticRegression())
    ])
    return pipeline.fit(X_train, y_train)

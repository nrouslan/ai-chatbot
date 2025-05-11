from natasha import Segmenter, NewsEmbedding, NewsMorphTagger, MorphVocab, Doc
from nltk import edit_distance

class TextPreprocessor:
    def __init__(self) -> None:
        # Инициализация моделей Natasha
        self.segmenter = Segmenter()
        self.embedding = NewsEmbedding()
        self.morph_tagger = NewsMorphTagger(self.embedding)
        self.morph_vocab = MorphVocab()

    def preprocess(self, text: str) -> str:
        """Предобработка текста (nlp)."""
        doc = Doc(text)
        doc.segment(self.segmenter)
        doc.tag_morph(self.morph_tagger)

        lemmas = []
        for token in doc.tokens:
            token.lemmatize(self.morph_vocab)
            lemmas.append(token.lemma)

        return ' '.join(lemmas)

def is_similar(text1: str, text2: str, threshold: float = 0.5) -> bool:
    """Проверяет, насколько текста схожи по расстоянию Левенштейна."""

    distance = edit_distance(text1, text2)
    return distance / max(len(text2), 1) <= threshold
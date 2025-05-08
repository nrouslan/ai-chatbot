from natasha import Segmenter, NewsEmbedding, NewsMorphTagger, MorphVocab, Doc

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

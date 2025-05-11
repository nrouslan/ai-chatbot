import speech_recognition as sr

from natasha import Segmenter, NewsEmbedding, NewsMorphTagger, MorphVocab, Doc
from nltk import edit_distance
from pydub import AudioSegment
from gtts import gTTS

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
    return edit_distance(text1, text2) / max(len(text2), 1) <= threshold

def text_to_voice(text: str, filename: str):
    """Конвертирует текстовое сообщение в голосовое."""
    tts = gTTS(text=text, lang='ru')
    tts.save(filename)
    
def voice_to_text(audio_path: str):
    """Конвертирует голосове сообщение в текстовое."""
    r = sr.Recognizer()
    try:
        with sr.AudioFile(audio_path) as source:
            audio = r.record(source)
            return r.recognize_google(audio, language="ru-RU")
    except sr.UnknownValueError:
        return None
    except sr.RequestError as e:
        print(f"Ошибка сервиса распознавания: {e}")
        return None
    except Exception as e:
        print(f"Неожиданная ошибка: {e}")
        return None

def convert_ogg_to_wav(ogg_path: str, wav_path: str):
    """Конвертирует OGG в WAV"""
    audio = AudioSegment.from_ogg(ogg_path)
    audio.export(wav_path, format="wav")

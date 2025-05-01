import speech_recognition as sr
from pydub import AudioSegment
from gtts import gTTS

def text_to_voice(text, filename):
    tts = gTTS(text=text, lang='ru')
    tts.save(filename)
    
def voice_to_text(audio_path):
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


def convert_ogg_to_wav(ogg_path, wav_path):
    """Конвертирует OGG в WAV"""
    audio = AudioSegment.from_ogg(ogg_path)
    audio.export(wav_path, format="wav")
    return wav_path
import os

from telegram import Update
from telegram.ext import CallbackContext

from bot.utils import create_book_keyboard
from ads.utils import get_book_recommendations
from nlp.answering import get_answer
from nlp.speech_recognition import text_to_voice, voice_to_text, convert_ogg_to_wav
from bot.constants import VOICE_DIR


async def start_command(update: Update, _: CallbackContext) -> None:
    await update.message.reply_text(
        'Привет! Я книжный бот. Я могу порекомендовать вам интересные книги. '
        'Просто напишите "Посоветуй книгу" или выберите жанр:',
        reply_markup=create_book_keyboard()
    )


async def help_command(update: Update, _: CallbackContext) -> None:
    help_text = (
        "Я могу:\n"
        "- Рекомендовать книги (просто напишите 'Посоветуй книгу')\n"
        "- Рассказать о конкретных книгах\n"
        "- Принимать голосовые сообщения\n"
        "- Помочь выбрать книгу по жанру\n\n"
        "Попробуйте сказать 'Какие у тебя есть фантастические книги?'"
    )
    await update.message.reply_text(help_text)


async def handle_text_message(update: Update, context: CallbackContext) -> None:
    replica = update.message.text
    
    # Получаем данные из context
    stats = context.bot_data['stats']
    dialogues = context.bot_data['dialogues']
    classifier = context.bot_data['classifier']
    vectorizer = context.bot_data['vectorizer']
    
    answer = get_answer(replica, stats, dialogues, classifier, vectorizer)
    
    # Обработка запросов на книги
    if 'книг' in replica.lower() or 'посоветуй' in replica.lower():
        answer = get_book_recommendations()
    
    await update.message.reply_text(answer, parse_mode='HTML')
   
    print(f"--> stats: {stats}")
    print(f"--> replica: {replica}")
    print(f"--> answer: {answer}\n")


async def handle_voice_message(update: Update, context: CallbackContext) -> None:
    voice_file = await context.bot.get_file(update.message.voice.file_id)
    ogg_path = os.path.join(VOICE_DIR, f"voice_{update.message.message_id}.ogg")
    wav_path = os.path.join(VOICE_DIR, f"voice_{update.message.message_id}.wav")
    
    await voice_file.download_to_drive(ogg_path)
    
    try:
        # Конвертируем OGG в WAV
        convert_ogg_to_wav(ogg_path, wav_path)
        
        # Распознаем текст
        text = voice_to_text(wav_path)
        
        if text:
            await update.message.reply_text(f"Вы сказали: {text}")

            # Получаем данные из context
            stats = context.bot_data['stats']
            dialogues = context.bot_data['dialogues']
            classifier = context.bot_data['classifier']
            vectorizer = context.bot_data['vectorizer']

            answer = get_answer(text, stats, dialogues, classifier, vectorizer)

            # Преобразуем ответ в голосовое сообщение
            voice_response_path = os.path.join(VOICE_DIR, f"response_{update.message.message_id}.mp3")
            text_to_voice(answer, voice_response_path)

            with open(voice_response_path, 'rb') as voice_file:
                await update.message.reply_voice(voice=voice_file)

            os.remove(voice_response_path)
        else:
            await update.message.reply_text("Извините, я не смог распознать ваше сообщение.")
    except Exception as e:
        await update.message.reply_text(f"Ошибка обработки голоса: {str(e)}")
    finally:
        # Удаляем временные файлы
        if os.path.exists(ogg_path):
            os.remove(ogg_path)
        if os.path.exists(wav_path):
            os.remove(wav_path)    


async def button_handler(update: Update, _: CallbackContext) -> None:
    query = update.callback_query
    await query.answer()
    
    if query.data.startswith('genre_'):
        genre = query.data.split('_')[1]
        if genre == 'any':
            response = get_book_recommendations()
        else:
            response = get_book_recommendations(genre)
        
        await query.edit_message_text(text=response, parse_mode='HTML')
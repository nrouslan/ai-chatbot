import os
from telegram import Update
from telegram.ext import CallbackContext

from bot import get_response_by_message_text, get_book_recommendations
from nlp import convert_ogg_to_wav, text_to_voice, voice_to_text
from constants import VOICE_DIR
from utils import get_genre_keyboard

async def start_command_handler(update: Update, _: CallbackContext) -> None:
    await update.message.reply_text(
        'Привет! Я книжный бот. Я могу порекомендовать вам интересные книги. '
        'Просто напишите "Посоветуй книгу" или выберите жанр:',
        reply_markup=get_genre_keyboard()
    )

async def help_command_handler(update: Update, _: CallbackContext) -> None:
    await update.message.reply_text(
        "Я могу:\n\n"
        "📚 Рекомендовать книги (просто напишите 'Посоветуй книгу')\n"
        "🔍 Рассказать о конкретных книгах (назовите автора или название)\n"
        "🎙️ Принимать голосовые сообщения (просто отправьте аудио)\n"
        "🌿 Помочь выбрать книгу по жанру (укажите предпочтения)\n\n"
        "💬 Что вас интересует?"
    )
    
async def message_text_handler(update: Update, context: CallbackContext) -> None:
    theme_history = context.bot_data.get('theme_history', [])

    # Получаем текст ответа
    response_text = get_response_by_message_text(
        update.message.text,
        context.bot_data['pipeline'],
        context.bot_data['intents_data'],
        context.bot_data['dialogues'],
        theme_history,
        context.bot_data['book_ads_data']['book_ads']
    )

    # Проверяем, нужно ли добавить клавиатуру
    if theme_history and theme_history[0] == 'book_selection':
        await update.message.reply_text(
            response_text,
            reply_markup=get_genre_keyboard()
        )
    else:
        await update.message.reply_text(response_text, parse_mode='HTML')

    # Дополнительное сообщение, если тема - реклама книги
    if theme_history and theme_history[0] == 'book_advertisement':
        book_recommendations = get_book_recommendations(
            context.bot_data['book_ads_data']['book_ads'], 
            update.message.text)
        await update.message.reply_text(book_recommendations, parse_mode='HTML')

async def voice_message_handler(update: Update, context: CallbackContext) -> None: 
    message_id = update.message.message_id
    ogg_path = os.path.join(VOICE_DIR, f"voice_{message_id}.ogg")
    wav_path = os.path.join(VOICE_DIR, f"voice_{message_id}.wav")
    response_path = os.path.join(VOICE_DIR, f"response_{message_id}.mp3")

    try:
        # Скачиваем голосовое сообщение
        voice = await context.bot.get_file(update.message.voice.file_id)
        await voice.download_to_drive(ogg_path)

        # Конвертируем и распознаём речь
        convert_ogg_to_wav(ogg_path, wav_path)
        text = voice_to_text(wav_path)

        if not text:
            await update.message.reply_text("Извините, я не смог распознать ваше сообщение.")
            return

        # Получаем ответ и преобразуем его в голос
        answer = get_response_by_message_text(
            text, 
            context.bot_data['pipeline'], 
            context.bot_data['intents_data'],
            context.bot_data['dialogues'],
            context.bot_data['theme_history'],
            context.bot_data['book_ads_data']['book_ads']
        )
        text_to_voice(answer, response_path)

        # Отправляем голосовой ответ
        with open(response_path, 'rb') as voice_file:
            await update.message.reply_voice(voice=voice_file)

    except Exception as e:
        await update.message.reply_text("Извините, произошла ошибка при обработке вашего сообщения.")
        print(f"--> Ошибка обработки голоса: {e}")

    finally:
        # Удаляем временные файлы
        for path in (ogg_path, wav_path, response_path):
            if os.path.exists(path):
                os.remove(path)

async def button_handler(update: Update, context: CallbackContext) -> None:
    book_ads_data = context.bot_data['book_ads_data']
    query = update.callback_query
    await query.answer()

    if query.data.startswith('genre_'):
        genre = query.data.split('_')[1]
        if genre == 'any':
            response = get_book_recommendations(book_ads_data['book_ads'])
        else:
            response = get_book_recommendations(book_ads_data['book_ads'], genre)

        await query.edit_message_text(text=response, parse_mode='HTML')

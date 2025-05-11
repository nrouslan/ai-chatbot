import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext

from bot import get_response_by_message_text
from nlp import convert_ogg_to_wav, text_to_voice, voice_to_text
from constants import VOICE_DIR

async def start_command_handler(update: Update, _: CallbackContext) -> None:
    await update.message.reply_text(
        'Привет! Я книжный бот. Я могу порекомендовать вам интересные книги. '
        'Просто напишите "Посоветуй книгу" или выберите жанр:',
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("Фантастика", callback_data='genre_fantasy')],
            [InlineKeyboardButton("Детектив", callback_data='genre_detective')],
            [InlineKeyboardButton("Бизнес", callback_data='genre_business')],
            [InlineKeyboardButton("Любой жанр", callback_data='genre_any')]
        ])
    )

async def help_command_handler(update: Update, _: CallbackContext) -> None:
    await update.message.reply_text(
        "Я могу:\n"
        "- Рекомендовать книги (просто напишите 'Посоветуй книгу')\n"
        "- Рассказать о конкретных книгах\n"
        "- Принимать голосовые сообщения\n"
        "- Помочь выбрать книгу по жанру\n\n"
    )
    
async def message_text_handler(update: Update, context: CallbackContext) -> None:        
    await update.message.reply_text(get_response_by_message_text(
        update.message.text, context.bot_data['pipeline'], context.bot_data['intents_data']))

async def voice_message_handler(update: Update, context: CallbackContext) -> None:    
    message_id = update.message.message_id

    ogg_path = os.path.join(VOICE_DIR, f"voice_{message_id}.ogg")
    wav_path = os.path.join(VOICE_DIR, f"voice_{message_id}.wav")

    voice_file = await context.bot.get_file(update.message.voice.file_id)
    await voice_file.download_to_drive(ogg_path)
    
    try:
        # Конвертируем OGG в WAV
        convert_ogg_to_wav(ogg_path, wav_path)
        
        # Распознаем текст
        text = voice_to_text(wav_path)
        
        if text:
            answer = get_response_by_message_text(text, context.bot_data['pipeline'], context.bot_data['intents_data'])

            # Преобразуем ответ в голосовое сообщение
            voice_response_path = os.path.join(VOICE_DIR, f"response_{message_id}.mp3")
            text_to_voice(answer, voice_response_path)

            with open(voice_response_path, 'rb') as voice_file:
                await update.message.reply_voice(voice=voice_file)

            os.remove(voice_response_path)
        else:
            await update.message.reply_text("Извините, я не смог распознать ваше сообщение.")
    except Exception as e:
        update.message.reply_text("Извините, я не смог распознать ваше сообщение.")
        print(f"--> Ошибка обработки голоса: {str(e)}")
    finally:
        # Удаляем временные файлы
        if os.path.exists(ogg_path):
            os.remove(ogg_path)
        if os.path.exists(wav_path):
            os.remove(wav_path) 

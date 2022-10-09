from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, ConversationHandler
from pytube import YouTube
import os, ssl


ADDRESS, FORMAT = range(2)

url = str()

def start(update, _):
    global url
    update.message.reply_text(
        'Введите адрес видео.\n'
        'Команда /cancel, чтобы выйти.\n'
        )
    
    return ADDRESS

def address(update, _):
    global url
    url = update.message.text

    reply_keyboard = [['Video', 'Audio']]
    markup_key = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True, resize_keyboard=True)
    
    update.message.reply_text(
        'Выберите формат загрузки.\n'
        'Команда /cancel, чтобы выйти.\n',
        reply_markup=markup_key)
    return FORMAT

def format(update, _):
    update.reply_markup=ReplyKeyboardRemove()
    global url
    res_format = update.message.text
    # На моем компьютере возникли проблемы с SSL-сертификатами, поэтому пришлось добавить следующий блок кода:
    if (not os.environ.get('PYTHONHTTPSVERIFY', '') and
        getattr(ssl, '_create_unverified_context', None)):
        ssl._create_default_https_context = ssl._create_unverified_context

    if res_format == "Video":
        YouTube(url).streams.filter(progressive=True, file_extension='mp4').order_by('resolution').desc().first().download()
        update.message.reply_text('Processing...')
        path = 'D:\GeekBrains\youtube_downloader_bot\\' + YouTube(url).title + '.mp4'
        update.message.reply_video(video=open(path, 'rb'))
    else:
        YouTube(url).streams.filter(only_audio=True).desc().first().download()
        path = 'D:\GeekBrains\youtube_downloader_bot\\' + YouTube(url).title + '.webm'
        update.message.reply_audio(audio=open(path, 'rb'))
        
    update.message.reply_text(
        '/start', 
        reply_markup=ReplyKeyboardRemove()
    )
    os.remove(path)
    return ConversationHandler.END
    

def cancel(update, _):
    update.message.reply_text(
        'До новых встреч!', 
        reply_markup=ReplyKeyboardRemove()
    )
    return ConversationHandler.END


updater = Updater('Токен')
    
dispatcher = updater.dispatcher

conv_handler = ConversationHandler(
    entry_points=[CommandHandler('start', start)],
    states={
        ADDRESS: [MessageHandler(Filters.text & ~Filters.command, address)],
        FORMAT: [MessageHandler(Filters.regex('^(Video|Audio)$'), format)]
    },
    fallbacks=[CommandHandler('cancel', cancel)],
)

dispatcher.add_handler(conv_handler)

updater.start_polling()
updater.idle()
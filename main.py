from telegram.ext import Updater, CommandHandler, MessageHandler, filters
import youtube_dl
import sys

def start(update, context):
    update.message.reply_text(
        "Hi, nice to see you here. Just paste your links and i will download for uu")

def dl(update, context):
    ytdl_argv = {'format': 'bestaudio/best',
                 'postprocessors': [{
                     'key': 'FFmpegExtractAudio',
                     'preferredcodec': 'mp3',
                     'preferredquality': '320',
                 }]
                 }
    with youtube_dl.YoutubeDL(ytdl_argv) as ytdl:
        ytdl.download([update.message.text])

token= sys.argv[1]
updater = Updater(token, use_context=True)


updater.dispatcher.add_handler(CommandHandler('start', start))
updater.dispatcher.add_handler(MessageHandler(filters.Filters.text, dl))

updater.start_polling()
updater.idle()
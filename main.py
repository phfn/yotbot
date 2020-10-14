from telegram.ext import Updater, CommandHandler, MessageHandler, filters
import youtube_dl
import sys
import re
import string
import random
import os


def random_string(length=5):
    ret=""
    for i in range(length):
        ret=ret+random.choice(string.ascii_letters)

    return ret
def start(update, context):
    update.message.reply_text(
        "Hi, nice to see you here. Just paste your links and i will download for uu")

def dl(update, context):
    path=random_string()
    print(path)
    ytdl_argv = {'format': 'bestaudio/best',
                 'postprocessors': [{
                     'key': 'FFmpegExtractAudio',
                     'preferredcodec': 'mp3',
                     'preferredquality': '192',
                 }],
                 "outtmpl": path+".webm"
                 }
    pat=re.compile("http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))")
    if pat.match(update.message.text):
        with youtube_dl.YoutubeDL(ytdl_argv) as ytdl:
            test=ytdl.download([update.message.text])
        with open(path+".mp3", "rb") as file:
            update.message.reply_audio(audio=file)
        os.remove(path+".mp3")
    else:
        update.message.reply_text("Well that didnt work")
token= sys.argv[1]
updater = Updater(token, use_context=True)

updater.dispatcher.add_handler(CommandHandler('start', start))
updater.dispatcher.add_handler(MessageHandler(filters.Filters.text, dl))

updater.start_polling()
updater.idle()
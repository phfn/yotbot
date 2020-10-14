from telegram.ext import Updater, CommandHandler, MessageHandler, filters
import youtube_dl
import sys
import re
import string
import random
import os
from mutagen.mp3 import MP3
from bs4 import BeautifulSoup, element, SoupStrainer
import requests
import urllib

def get_video_title(url):
    soup = BeautifulSoup(requests.get(url).text, features="html.parser", parse_only=SoupStrainer("title"))

def random_string(length=5):
    ret=""
    for i in range(length):
        ret=ret+random.choice(string.ascii_letters)

    return ret
def start(update, context):
    update.message.reply_text(
        "Hi, nice to see you here. Just paste your links and i will download for uu")
def ytdl(url, preferredquality=320):
    path = random_string()
    print(path)
    ytdl_argv = {'format': 'bestaudio/best',
                 'postprocessors': [{
                     'key': 'FFmpegExtractAudio',
                     'preferredcodec': 'mp3',
                     'preferredquality': str(preferredquality),
                 }],
                 "forcetitle": "",
                 "outtmpl": path + ".webm"
                 }
    with youtube_dl.YoutubeDL(ytdl_argv) as ytdl:
        ytdl.download([url])
    return path



def dl(update, context):
    pat = re.compile("http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))")
    if pat.match(update.message.text):
        path=ytdl(update.message.text)
        if os.stat(path + ".mp3").st_size > 50_000_000:
            path = ytdl(update.message.text, 192)
            if os.stat(path + ".mp3").st_size > 50_000_000:
                path = ytdl(update.message.text, 128)
                if os.stat(path + ".mp3").st_size > 50_000_000:
                    update.message.reply_text("Die Datei war leider zu Groß")
        print(os.stat(path+".mp3").st_size)

        with open(path+".mp3", "rb") as file:
            update.message.reply_audio(audio=file)
        os.remove(path+".mp3")
    else:
        update.message.reply_text("Well that didnt work")
    print("finisch")
token= sys.argv[1]
updater = Updater(token, use_context=True)

updater.dispatcher.add_handler(CommandHandler('start', start))
updater.dispatcher.add_handler(MessageHandler(filters.Filters.text, dl))

updater.start_polling()
updater.idle()
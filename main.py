from telegram.ext import Updater, CommandHandler, MessageHandler, filters
import youtube_dl
import sys
import re
import string
import random
import os
import requests
from mutagen.mp3 import MP3 as mp3_tags


def random_string(length=5):
    ret = ""
    for i in range(length):
        ret = ret + random.choice(string.ascii_letters)
    return ret


def start(update, context):
    update.message.reply_text(
        "Hi, nice to see you here. Just paste your links and i will download for u")


def ytdl(url, preferredquality=320):
    path = random_string()
    print(path)
    ytdl_argv = {'format': 'bestaudio/best',
                 'writethumbnail': True,
                 'postprocessors': [{
                     'key': 'FFmpegExtractAudio',
                     'preferredcodec': 'mp3',
                     'preferredquality': str(preferredquality),
                 },
                     {'key': 'EmbedThumbnail'},
                     {'key': 'FFmpegMetadata'}
                 ],
                 "forcetitle": "",
                 "outtmpl": path + ".webm"
                 }
    with youtube_dl.YoutubeDL(ytdl_argv) as ytdl:
        ytdl.download([url])

    # rename file to title
    new_path = str(mp3_tags(path + ".mp3")["TIT2"])
    os.rename(path + ".mp3", new_path + ".mp3")
    path = new_path
    return path


def dl(update, context):
    # check if message is a valid url
    pat = re.compile("http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))")
    if pat.match(update.message.text):

        path = ytdl(update.message.text)

        # if file if to big (50mb) teegram wont send it
        if os.stat(path + ".mp3").st_size > 50_000_000:
            path = ytdl(update.message.text, 192)
            if os.stat(path + ".mp3").st_size > 50_000_000:
                path = ytdl(update.message.text, 128)
                if os.stat(path + ".mp3").st_size > 50_000_000:
                    path = ytdl(update.message.text, 64)
                    if os.stat(path + ".mp3").st_size > 50_000_000:
                        update.message.reply_text("Die Datei war leider zu Groß")

        with open(path + ".mp3", "rb") as file:
            update.message.reply_audio(audio=file)
        os.remove(path + ".mp3")
    else:
        update.message.reply_text("Well that didnt work")
    print("finisch")


token = sys.argv[1]

updater = Updater(token, use_context=True)

updater.dispatcher.add_handler(CommandHandler('start', start))
updater.dispatcher.add_handler(MessageHandler(filters.Filters.text, dl))

updater.start_polling()
updater.idle()

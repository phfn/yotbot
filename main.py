from telegram.ext import Updater, CommandHandler, MessageHandler, filters
import telegram
import youtube_dl
import sys
import re
import string
import random
import os
import requests
from mutagen.mp3 import MP3 as mp3_tags


def get_valid_filename(s):
    """
    stolen at django utils text
    Return the given string converted to a string that can be used for a clean
    filename. Remove leading and trailing spaces; convert other spaces to
    underscores; and remove anything that is not an alphanumeric, dash,
    underscore, or dot.
    >>> get_valid_filename("john's portrait in 2004.jpg")
    'johns_portrait_in_2004.jpg'
    """
    # s = str(s).strip().replace(' ', '_')
    return re.sub(r'(?u)[^-\w.]', '', s)


def random_string(length=5):
    ret = ""
    for i in range(length):
        ret = ret + random.choice(string.ascii_letters)
    return ret


def start(update, context):
    update.message.reply_text(
        "Hi, nice to see you here. Just paste your links and i will download for u")


def ytdl(url, path, preferredquality=320):
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
                 "keepvideo": True,
                 "forcetitle": True,
                 "outtmpl": path + ".webm"
                 }
    with youtube_dl.YoutubeDL(ytdl_argv) as ytdl:
        ytdl.download([url])


    return path


def dl(update: telegram.update.Update, context):
    # check if message is a valid url
    pat = re.compile("http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))")
    url=update.message.text
    if pat.match(url):
        path = random_string()
        ytdl(url, path)

        # if file if to big (50mb) teegram wont send it
        if os.stat(path + ".mp3").st_size > 50_000_000:
            update.message.reply_text("oh, thats a long vid. Could take a while, but i'll try my best")
            os.remove(path + ".mp3")
            ytdl(url, path, 192)
            if os.stat(path + ".mp3").st_size > 50_000_000:
                os.remove(path + ".mp3")
                ytdl(url, path, 128)
                if os.stat(path + ".mp3").st_size > 50_000_000:
                    os.remove(path + ".mp3")
                    path = ytdl(update.message.text, 64)
                    if os.stat(path + ".mp3").st_size > 50_000_000:
                        os.remove(path + ".mp3")
                        update.message.reply_text("Die Datei war leider zu Groß")
        os.remove(path+".webm")

        # rename file to title
        new_path = get_valid_filename(str(mp3_tags(path + ".mp3")["TIT2"]))
        try:
            os.rename(path + ".mp3", new_path + ".mp3")
        except FileExistsError:
            os.remove(new_path + ".mp3")
            os.rename(path + ".mp3", new_path + ".mp3")
        path = new_path
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

updater.start_polling(timeout=30)
updater.idle()

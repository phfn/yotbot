from telegram.ext import Updater, CommandHandler, MessageHandler, filters, run_async
import telegram
import youtube_dl
import sys
import re
import string
import random
import os
from mutagen.mp3 import MP3 as mp3_tags


def pprint(path, str, end="\n"):
    print(f"[{path}]{str}")

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
    return re.sub(r'(?u)[^-\w\s.]', '', s)


def random_string(length=5):
    ret = ""
    for i in range(length):
        ret = ret + random.choice(string.ascii_letters)
    return ret


def start(update, context):
    update.message.reply_text(
        "Hi, nice to see you here. Just paste your links and i will download for u")
def help(update, context):
    update.message.reply_text(
        "Just paste your links here and i will send you a file back. "
        "If the file is to big (Telegram blocks bot messages > 50 MB) i will try to reduce the bitrate (quality) of the File. For good quality keep the length under 1 hour"
        "If you have any further questions, suggestions, bugs, feature requests, feel free to visit github.com/phfn/yotbot or via @hphfn08"
        "- Paul"
    )
def about(update, context):
    update.message.reply_text("Hi, i'm paul (@phfn08), and i wrote this bot. I hope you like it. If you want to know more about the YOTBot visi github.com/phfn/yotbot"
                              "A huge thanks to all the libaries i used: "
                              "youtube-dl (managing all the downloads)"
                              "telgram-bot-python (managing all the telegramm specific stuff, i don't wanna handle)"
                              "mutagen (handeling some of the Tagging stuff)"
                              "and to @clevero")


def ytdl(url, path, preferredquality=320, forcetitle=True, quiet=True):
    print(f"[{path}]", end="")
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
                 "forcetitle": forcetitle,
                 "quiet": quiet,
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
        bitrates=[320, 192, 124, 64, 32, 16, 8]
        FileSmallEnough=False
        for bitrate in bitrates:
            pprint(path, "trying "+str(bitrate)+"...")
            try:
                ytdl(url, path, bitrate, forcetitle=bitrate==320)
            except youtube_dl.utils.DownloadError:
                update.message.reply_text("There was a Problem downloading the Video. Pleas try again later. If this occurs regulary write it to github.com/phfn/yotbot thx")

            pprint(path, f"filesize@{bitrate}="+str(os.stat(path + ".mp3").st_size/1024/1024))
            if os.stat(path + ".mp3").st_size < 50_000_000:
                FileSmallEnough=True
                break
        os.remove(path+".webm")
        if not FileSmallEnough:
            update.message.reply_text("File was to big. I'm sry :/")

        # rename file to title
        new_path = get_valid_filename(str(mp3_tags(path + ".mp3")["TIT2"]))
        try:
            os.rename(path + ".mp3", new_path + ".mp3")
        except FileExistsError:
            os.remove(new_path + ".mp3")
            os.rename(path + ".mp3", new_path + ".mp3")
        new_path
        with open(new_path + ".mp3", "rb") as file:
            update.message.reply_audio(audio=file)
        os.remove(new_path + ".mp3")
    else:
        update.message.reply_text("Well that didnt work")

    pprint(path, "finisch")


token = sys.argv[1]

updater = Updater(token, use_context=True)

updater.dispatcher.add_handler(CommandHandler('start', start, run_async=True))
updater.dispatcher.add_handler(CommandHandler('help', help, run_async=True))
updater.dispatcher.add_handler(CommandHandler('about', about, run_async=True))
updater.dispatcher.add_handler(MessageHandler(filters.Filters.text, dl, run_async=True))

updater.start_polling(timeout=30)
updater.idle()

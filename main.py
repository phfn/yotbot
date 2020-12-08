from telegram.ext import Updater, CommandHandler, MessageHandler, filters, run_async
import telegram
import youtube_dl
import sys
import re
import string
import random
import os
import json
import requests
import datetime
from mutagen.mp3 import MP3 as mp3_tags
from urllib.error import HTTPError, URLError

MAX_VIDEO_LENGTH = 240 * 60


def pprint(path, str, end="\n"):
    print(f"{datetime.datetime.now()}[{path}]{str}", end=end)


def get_length_of_video(url):
    with youtube_dl.YoutubeDL({"skip_download": True, "quiet": True}) as ytdl:
        duration = ytdl.extract_info(url)['duration']
    return duration


def get_valid_filename(s):
    """
    stolen at django utils text, but spacec allowed
    Return the given string converted to a string that can be used for a clean
    filename. Remove leading and trailing spaces; and remove anything that is not an alphanumeric, dash,
    underscore, or dot.
    >>> get_valid_filename("EINKAUFEN! - Minecraft [Deutsch/HD]")
    'EINKAUFEN - Minecraft DeutschHD'
    """
    # s = str(s).strip().replace(' ', '_')
    return re.sub(r'(?u)[^-\w\s.]', '', s)


def random_string(length=5):
    ret = ""
    for i in range(length):
        ret = ret + random.choice(string.ascii_letters)
    return ret


def command_start(update, context):
    update.effective_message.reply_text(
        "Hi, nice to see you here. Just paste your links and i will download for u")


def command_help(update: telegram.Update, context):
    update.effective_message.reply_text(
        "Just paste your links here and i will send you a file back.\n"
        "In groups add the bot and write /dl@yotBot https://www.youtube.com/watch?v=umnULvgEv5Q"
        "If the file is to big (Telegram blocks bot messages > 50 MB) i will try to reduce the bitrate (quality) of the File. For good quality keep the length under 1 hour\n"
        f"Our maximum video Limit is {int(MAX_VIDEO_LENGTH / 60)}min.\n"
        "You can download nearly every Video from nearly every site\n"
        "If you have any further questions, suggestions, bugs, feature requests, feel free to visit github.com/phfn/yotbot or via @phfn08\n"
        "- Paul"
    )


def command_about(update, context):
    update.effective_message.reply_text(
        "Hi, i'm paul (@phfn08), and i wrote this bot cuz its fun (and i wanted to use it). I hope you like it. If you want to know more about the YOTBot visit github.com/phfn/yotbot \n"
        "A huge thanks to all the libaries i used:\n"
        "youtube-dl (managing all the downloads)\n"
        "telgram-bot-python (managing all the telegramm specific stuff, i don't wanna handle)\n"
        "mutagen (handeling some of the tagging stuff)\n"
        "and to @Clevero\n")


def command_dl(update, context):
    if len(update.effective_message.text.split(" ")) < 2:
        update.effective_message.reply_text(
            "Please senda link togeather. for example /dl@yotBot https://www.youtube.com/watch?v=BX6KILafIS0")
        return
    url = update.effective_message.text.split(" ")[1]
    pat = re.compile("http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))")
    if pat.match(url):
        download_video(update, url)
    else:
        update.effective_message.reply_text("I think that was no link. :/ try /search ")
        pprint(update.effective_message.text, "is no link")


def command_search(update: telegram.Update, context):
    if len(update.effective_message.text.split(" ")) < 2:
        update.effective_message.reply_text(
            "Please senda query togeather. for example /search hammerfall")
        return
    query = update.effective_message.text.split(" ", maxsplit=1)[1]
    ytdl_argv = {
        'default_search': "ytsearch",
        "skip_download": True,
        "quiet": True
    }
    with youtube_dl.YoutubeDL({'default_search': "ytsearch", "skip_download": True, "quiet": True}) as ytdl:
        results = ytdl.extract_info(query)


    if len(results["entries"]) <= 0:
        update.effective_message.reply_text(f"I didn't found any video for {query} :/")
        return

    id = results["entries"][0]["id"]
    video_url = f"https://youtube.com/watch?v={id}"

    download_video(update, url=video_url)


def youtube_dl_wrapper(url, path, preferredquality=320, forcetitle=True, quiet=True):
    ytdl_argv = {'format': 'bestaudio/best',  # download audio in best quality
                 'writethumbnail': True,  # download thumbnail
                 'postprocessors': [{
                     'key': 'FFmpegExtractAudio',
                     'preferredcodec': 'mp3',
                     'preferredquality': str(preferredquality),
                 },
                     {'key': 'EmbedThumbnail'},  # add thumbnail to mp3 file
                     {'key': 'FFmpegMetadata'}  # add metadata to mp3 file
                 ],
                 "keepvideo": True,  # keep the video after converting to mp3
                 "quiet": quiet,  # dont print everythin
                 "outtmpl": path + ".webm"  # outputtemplate
                 }
    with youtube_dl.YoutubeDL(ytdl_argv) as ytdl:
        ytdl.download([url])
    return path


def download_video(update: telegram.update.Update, url):
    path = random_string()
    pprint(path, f"download_video: {url}")
    update.effective_chat.send_action(telegram.chataction.ChatAction.UPLOAD_AUDIO)
    bitrates = [320, 192, 124, 64, 32, 16, 8]
    FileSmallEnough = False
    for bitrate in bitrates:
        pprint(path, "trying " + str(bitrate) + "...")
        try:
            if get_length_of_video(url) > MAX_VIDEO_LENGTH:
                update.effective_message.reply_text(
                    f"Your Video is to long. Our maximum video Limit is {int(MAX_VIDEO_LENGTH / 60)}min")
                pprint(path, "Video to long")
                return

            youtube_dl_wrapper(url, path, bitrate, forcetitle=bitrate == 320)
        except youtube_dl.utils.DownloadError as err:
            if type(err.exc_info[1]) == HTTPError and err.exc_info[1].code == 404 or \
                    type(err.exc_info[1]) == URLError:
                update.effective_message.reply_text("I couldn't find this site")
                return

            update.effective_message.reply_text(
                "There was a problem downloading the Video. Please try again later. If this occurs regulary write it to github.com/phfn/yotbot or text me @phfn08, thx")
            return

        pprint(path, f"filesize@{bitrate}=" + str(os.stat(path + ".mp3").st_size / 1024 / 1024))
        if os.stat(path + ".mp3").st_size < 50_000_000:
            FileSmallEnough = True
            break
    os.remove(path + ".webm")
    if not FileSmallEnough:
        update.effective_message.reply_text("File was to big. I'm sry :/")

    # rename file to title
    new_path = get_valid_filename(str(mp3_tags(path + ".mp3")["TIT2"]))
    try:
        os.rename(path + ".mp3", new_path + ".mp3")
    except FileExistsError:
        os.remove(new_path + ".mp3")
        os.rename(path + ".mp3", new_path + ".mp3")

    with open(new_path + ".mp3", "rb") as file:
        update.effective_message.reply_audio(audio=file)
    os.remove(new_path + ".mp3")
    pprint(path, "finisch")


def message_handler(update: telegram.Update, contexts):
    pat = re.compile("http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))")
    if pat.match(update.effective_message.text):
        download_video(update, update.effective_message.text)
    else:
        update.effective_message.reply_text("I think that was no link. :/ try /search ")
        pprint(update.effective_message.text, "is no link")


token = os.getenv(key="TG_BOT_TOKEN")
updater = Updater(token, use_context=True)

updater.dispatcher.add_handler(CommandHandler('start', command_start, run_async=True))
updater.dispatcher.add_handler(CommandHandler('help', command_help, run_async=True))
updater.dispatcher.add_handler(CommandHandler('about', command_about, run_async=True))
updater.dispatcher.add_handler(CommandHandler('dl', command_dl, run_async=True))
updater.dispatcher.add_handler(CommandHandler('search', command_search, run_async=True))
updater.dispatcher.add_handler(CommandHandler('s', command_search, run_async=True))
updater.dispatcher.add_handler(MessageHandler(filters.Filters.text, message_handler, run_async=True))

updater.start_polling(timeout=10)
updater.idle()

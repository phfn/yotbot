import traceback
import argparse
from Video import Video
from telegram.ext import Updater, CommandHandler, MessageHandler, filters, run_async
import telegram
import yt_dlp as youtube_dl
import re
import os
import json
import datetime
from urllib.error import HTTPError, URLError
import logging
from yotbot_utils import get_links
import configargparse
from dotenv import load_dotenv

MAX_VIDEO_LENGTH = 240 * 60

load_dotenv()
parser = configargparse.ArgumentParser()
parser.add_argument("--botname", help="the telegram name of your bot", env_var="TG_BOT_NAME", required=True)
parser.add_argument("--token", help="the token you got from @botfather", env_var="TG_BOT_TOKEN", required=True)
parser.add_argument("--responses", help="a json file containing all response textes", default="responses.json")
parser.add_argument("--verbose", "-v", help="increase output verbosity", action="store_true")
parser.add_argument("--log", help="write a log file")
args = parser.parse_args()
if args.verbose:
    print(f"config = {args.__dict__}")

response_path = args.responses
botname = args.botname

logger = logging.getLogger("yotbot")
logger.setLevel(logging.DEBUG)

ch = logging.StreamHandler()
ch.setFormatter(logging.Formatter(f'[%(name)s]%(levelname)s:%(message)s'))
ch.setLevel(logging.DEBUG if args.verbose else logging.INFO)
logger.addHandler(ch)

if args.log is not None:
    fh = logging.FileHandler(args.log)
    fh.setFormatter(logging.Formatter('[%(name)s]%(asctime)s:%(levelname)s:%(message)s'))
    fh.setLevel(logging.DEBUG)
    logger.addHandler(fh)

with open(response_path) as file:
    response_texts = json.load(file)


def pprint(path, str, end="\n"):
    print(f"{datetime.datetime.now()}[{path}]{str}", end=end)


def command_start(update, context):
    update.effective_message.reply_text(
        "Hi, nice to see you here. Just paste your links and i will download for u")


def command_help(update: telegram.Update, context):
    update.effective_message.reply_text(
        response_texts["help"].replace("{limit}", f"{int(MAX_VIDEO_LENGTH / 60)}").replace("{botname}", botname))


def command_about(update, context):
    update.effective_message.reply_text(response_texts["about"])


def command_dl(update, context):
    message = update.effective_message
    if len(message.text.split(" ")) < 2:
        message.reply_text(response_texts["dl"].replace("{botname}", botname))
        return
    links = get_links(message.text)
    for link in links:
        download_video(update, link)
    if not links:
        message.reply_text(response_texts["not_an_url"])
        pprint(message.text, "is no link")


def command_search(update: telegram.Update, context):
    if len(update.effective_message.text.split(" ")) < 2:
        update.effective_message.reply_text(response_texts["search"])
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
        update.effective_message.reply_text(response_texts["vid_not_found"])
        return

    video_id = results["entries"][0]["id"]
    video_url = f"https://youtube.com/watch?v={video_id}"

    download_video(update, url=video_url)


def download_video(update: telegram.update.Update, url):
    vid = Video(url)
    path = vid.get_subdir()
    logger.info(f"download_video: {url}")
    update.effective_chat.send_action(telegram.chataction.ChatAction.UPLOAD_AUDIO)
    bitrates = [320, 256, 192, 160, 128, 96, 64, 32, 16, 8]
    file_small_enough = False
    for bitrate in bitrates:
        vid.logger.debug(f"trying {bitrate}...")
        try:
            if vid.get_length() > MAX_VIDEO_LENGTH:
                update.effective_message.reply_text(
                    response_texts["vid_to_long"].replace("{limit}", {int(MAX_VIDEO_LENGTH / 60)}))
                vid.logger.debug("Video to long")
                return

            mp3_file = vid.download_mp3(bitrate)
        except youtube_dl.utils.DownloadError as err:
            send_log = False
            if type(err.exc_info[1]) == HTTPError and err.exc_info[1].code == 404:
                error_message = response_texts["404"]
            elif type(err.exc_info[1]) == HTTPError and err.exc_info[1].code == 429:
                error_message = response_texts["429"]
            elif "The uploader has not made this video available in your country" in str(err)\
                    or "This video is not available" in str(err):
                error_message = response_texts["geoblock"]
            elif "Unsupported URL" in str(err):
                error_message = response_texts["unsupported"]
            elif "This video is only available to Music Premium members" in str(err):
                error_message = response_texts["premium"]
            else: #Only if i dont know the reason why ytdl is failing
                error_message = response_texts["ytdl_problem"]
                send_log = True
                logger.warning(traceback.format_exc())
                logger.warning(err)


            logger.info("failed")

            if send_log:
                with open(vid.log_path) as log_file:
                    update.effective_message.reply_document(log_file)

            update.effective_message.reply_text(error_message)

            vid.clear()
            return

        vid.logger.debug(f"filesize@{bitrate}=" + str(os.stat(mp3_file).st_size / 1024 / 1024))
        if os.stat(mp3_file).st_size < 50_000_000:
            file_small_enough = True
            break

    if not file_small_enough:
        update.effective_message.reply_text(response_texts["file_to_big"])

    with open(mp3_file, "rb") as file:
        update.effective_message.reply_audio(audio=file)

    vid.clear()
    logger.info("finisch")



def message_handler(update: telegram.Update, contexts):
    links = get_links(update.effective_message.text)
    for link in links:
        download_video(update, link)


updater = Updater(args.token, use_context=True)

updater.dispatcher.add_handler(CommandHandler('start', command_start, run_async=True))
updater.dispatcher.add_handler(CommandHandler('help', command_help, run_async=True))
updater.dispatcher.add_handler(CommandHandler('about', command_about, run_async=True))
updater.dispatcher.add_handler(CommandHandler('dl', command_dl, run_async=True))
updater.dispatcher.add_handler(CommandHandler('search', command_search, run_async=True))
updater.dispatcher.add_handler(CommandHandler('s', command_search, run_async=True))
updater.dispatcher.add_handler(MessageHandler(filters.Filters.text, message_handler, run_async=True))

updater.start_polling(timeout=10)
updater.idle()

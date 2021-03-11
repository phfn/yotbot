import shutil

import youtube_dl
import os
import yotbot_utils
from mutagen.mp3 import MP3
from mutagen import MutagenError
import logging
from importlib import reload
os.environ["PYTHONUNBUFFERED"]="1"

class Video:

    def __init__(self, video_url, working_dir="videos"):
        self.url = video_url
        self.downloaded = False
        self.subdir = yotbot_utils.get_random_string()
        self.path = working_dir + "/" + self.subdir
        os.makedirs(self.path)
        self.title = self.subdir
        reload(logging)
        logging.basicConfig(filename=self.path+"/video.log", format='%(asctime)s:%(levelname)s:%(message)s', level=logging.DEBUG)
        logging.info(f"url={self.url}")
        logging.info(f"subdir={self.subdir}")
        logging.info(f"path={self.path}")

    def get_length(self):
        logging.info("get_length:")
        #Try to find out with mutagen
        if(self.downloaded):
            return MP3(self.get_full_mp3_path()).get(key="length", default=-1)

        #Try to find out with ytdl
        with youtube_dl.YoutubeDL({"skip_download": True, "quiet": True}) as ytdl:
            try:
                duration = ytdl.extract_info(self.url)['duration']
                logging.info(f"length={duration}")
            except KeyError:
                duration = -1
                logging.info(f"legth was not found, probebly cuz its no YT Video")
            except youtube_dl.utils.DownloadError as err:
                logging.warning(str(err))
                raise err
            return duration

    def get_full_mp3_path(self):
        if not self.downloaded: raise FileNotFoundError
        return self.path+"/"+self.title+".mp3"

    def get_subdir(self):
        return self.subdir

    def download_mp3(self, bitrate=320):
        logging.info(f"downloading...")
        logging.info(f"bitrate={bitrate}")
        ytdl_argv = {'format': 'bestaudio/best',  # download audio in best quality
                     'writethumbnail': True,  # download thumbnail
                     'postprocessors': [{
                         'key': 'FFmpegExtractAudio',
                         'preferredcodec': 'mp3',
                         'preferredquality': str(bitrate),
                     },
                         {'key': 'EmbedThumbnail'},  # add thumbnail to mp3 file
                         {'key': 'FFmpegMetadata'}  # add metadata to mp3 file
                     ],
                     "keepvideo": True,  # keep the video after converting to mp3
                     "quiet": True,  # dont print everythin
                     "outtmpl": f"{self.path}/video.webm"  # outputtemplate
                     }
        with youtube_dl.YoutubeDL(ytdl_argv) as ytdl:
            try:
                ytdl.download([self.url])
                logging.info("download finished")
            except youtube_dl.utils.DownloadError as err:
                logging.warning("download failed")
                logging.warning(err)
                raise err

        try:
            self.title = yotbot_utils.get_valid_filename(str(MP3(f"{self.path}/video.mp3")["TIT2"]))
        except MutagenError:
            logging.info("could not retrieve mp3 tags")
            self.title = "video"

        mp3_path = shutil.move(f"{self.path}/video.mp3", f"{self.path}/{self.title}.mp3")
        logging.info(f"moved to {mp3_path}")
        return mp3_path

    def clear(self, keep_log=False):
        logging.info("clearing")
        if not keep_log:
            shutil.rmtree(self.path)

        for file in os.scandir(self.path):
            if file.name != "video.log":
                os.remove(file)


if __name__ == "__main__":
    url = "https://www.ringtoneshub.org/wp-content/uploads/2020/02/The-Life-of-Ram-BGM-Guitar-Ringtone.mp3"
    # url="https://www.youtube.com/watch?v=m70jMUxuUsQ"
    #  url="http://localhost:5000"
    vid = Video(url)
    #print(vid.get_legth())
    vid.download_mp3()
    vid.clear(keep_log=True)

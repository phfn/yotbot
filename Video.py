import shutil

import yt_dlp as youtube_dl
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

        # init dirs
        self.subdir = yotbot_utils.get_random_string()
        self.path = os.path.join(working_dir, self.subdir)
        self.log_path = os.path.join(self.path, "download_log.txt")
        os.makedirs(self.path)
        self.title = self.subdir
        
        # init logging
        self.logger = logging.getLogger(f"yotbot.video.{self.subdir}")
        self.logger.setLevel(logging.DEBUG)

        fh = logging.FileHandler(self.log_path)
        fh.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(message)s'))
        fh.setLevel(logging.DEBUG)
        self.logger.addHandler(fh)

        self.logger.debug(f"url={self.url}")
        self.logger.debug(f"subdir={self.subdir}")
        self.logger.debug(f"path={self.path}")

        # this is a workaround for ytdl not to print out error messages, that i catch
        self.ytdl_log = logging.getLogger("youtube-dl-logger")
        self.ytdl_log.setLevel(logging.CRITICAL)

    def get_length(self):
        self.logger.debug("get_length:")
        #Try to find out with mutagen
        if(self.downloaded):
            duration = MP3(self.get_full_mp3_path()).get(key="length", default=-1)

        else:
            #Try to find out with ytdl
            with youtube_dl.YoutubeDL({"skip_download": True, "quiet": True, "logger": self.ytdl_log}) as ytdl:
                try:
                    duration = ytdl.extract_info(self.url)['duration']
                except KeyError:
                    duration = -1
                    self.logger.debug("legth was not found, probebly cuz its no YT Video")
                except youtube_dl.utils.YoutubeDLError as err:
                    self.logger.debug(str(err))
                    duration = -1

        self.logger.debug(f"length={duration}")
        return duration

    def get_full_mp3_path(self):
        if not self.downloaded: raise FileNotFoundError
        return self.path+"/"+self.title+".mp3"

    def get_subdir(self):
        return self.subdir

    def get_path(self):
        return self.path

    def download_mp3(self, bitrate=320):
        self.logger.debug(f"downloading...")
        self.logger.debug(f"bitrate={bitrate}")

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
                     "logger": self.ytdl_log,
                     "outtmpl": f"{self.path}/video.webm"  # outputtemplate
                     }
        with youtube_dl.YoutubeDL(ytdl_argv) as ytdl:
            try:
                ytdl.download([self.url])
                self.logger.debug("download finished")
            except youtube_dl.utils.DownloadError as err:
                self.logger.debug(err)
                self.logger.debug("download failed")
                raise err

        try:
            self.title = yotbot_utils.get_valid_filename(str(MP3(f"{self.path}/video.mp3")["TIT2"]))
        except MutagenError:
            self.logger.debug("could not retrieve mp3 tags")
            self.title = "video"

        mp3_path = shutil.move(f"{self.path}/video.mp3", f"{self.path}/{self.title}.mp3")
        self.logger.debug(f"moved to {mp3_path}")
        return mp3_path

    def clear(self, keep_log=False):
        self.logger.debug("clearing, keep_log=%s", keep_log)
        for handler in self.logger.handlers:
            handler.close()
        if not keep_log:
            shutil.rmtree(self.path)
        else:
            for file in os.scandir(self.path):
                if file.path != self.log_path:
                    os.remove(file)


if __name__ == "__main__":
    #  url = "https://www.ringtoneshub.org/wp-content/uploads/2020/02/The-Life-of-Ram-BGM-Guitar-Ringtone.mp3"
    url="https://www.youtube.com/watch?v=m70jMUxuUsQ"
    #  url="http://localhost:5000"
    vid = Video(url)
    l = vid.get_length()
    print(l)
    #print(vid.get_legth())
    vid.download_mp3()
    #  vid.clear(keep_log=True)

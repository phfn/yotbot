import shutil

import youtube_dl
import os
import yotbot_utils
from mutagen.mp3 import MP3
from mutagen import MutagenError


class Video:

    def __init__(self, video_url, working_dir="videos"):
        self.url = video_url
        self.downloaded = False
        self.subdir = yotbot_utils.get_random_string()
        self.path = working_dir + "/" + self.subdir
        os.mkdir(self.path)
        self.title = self.subdir

    def get_legth(self):
        with youtube_dl.YoutubeDL({"skip_download": True, "quiet": True}) as ytdl:
            try:
                duration = ytdl.extract_info(self.url)['duration']
            except KeyError:
                duration = -1
            return duration

    def get_subdir(self):
        return self.subdir

    def download_video(self):
        ytdl_argv = {'format': 'bestaudio/best',  # download audio in best quality
                     'writethumbnail': True,  # download thumbnail
                     "quiet": True,  # dont print everythin
                     "outtmpl": f"{self.subdir}/video.webm"  # outputtemplate
                     }
        with youtube_dl.YoutubeDL(ytdl_argv) as ytdl:
            ytdl.download([self.url])

    def download_mp3(self, bitrate=320):
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
            print(ytdl.download([self.url]))


        try:
            self.title=yotbot_utils.get_valid_filename(str(MP3(f"{self.path}/video.mp3")["TIT2"]))
        except MutagenError:
            self.title="video"
        mp3_path = shutil.move(f"{self.path}/video.mp3", f"{self.path}/{self.title}.mp3")
        return mp3_path

    def clear(self):
        shutil.rmtree(self.path)




if __name__ == "__main__":

    url = "https://www.ringtoneshub.org/wp-content/uploads/2020/02/The-Life-of-Ram-BGM-Guitar-Ringtone.mp3"
    # url="https://www.youtube.com/watch?v=m70jMUxuUsQ"

    vid = Video(url)
    print(vid.get_legth())
    print(vid.download_mp3())
    vid.clear()

import youtube_dl
path="test"
preferredquality=320
url="https://www.youtube.com/watch?v=BX6KILafIS0"
youtube_dl.main(
        ["--extract-audio",
         "--audio-format", "mp3",
         "--add-metadata",
         "--embed-thumbnail",
         "--audio-quality", str(preferredquality),
         "-o", path + ".webm",
         url])
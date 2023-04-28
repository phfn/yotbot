# YOTbot - YouTube Over Telegram
HeyHo this is a Telegram Bot for downloading YouTube videos as MP3 Files.
It's running at [YOTBot](https://telegram.me/yotbot)
 

## Requirements
You have to install all packages mentioned in the requirements.txt. Also you need ffmpeg
```bash
pip install -r requirements.txt
```

## Settings
You have to specify the token you got from [BotFather](https://telegram.me/BotFather) and the name the bot should interact as.
You can specify them by setting environment variable or by passing them via cli
```bash
export TG_BOT_TOKEN="969855739:AAEqhAK5peBt42I7Z4FqsOFxGQO818ja768"
export TG_BOT_NAME="my_wonderfull_download_bot"
```
Also there is support for .env files.

```bash
python YOTBot.py --botname my_wonderfull_download_bot --token "969855739:AAEqhAK5peBt42I7Z4FqsOFxGQO818ja768"
```

To customize the messages the bot writes, you need to modify responses.json.

## Container
There is support to build a Container image
```bash
docker build -f Containerfile -t yotbot . && docker run yotbot
# or
docker-compose up --build
```

## Licence
GPL 3

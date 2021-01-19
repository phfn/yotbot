# YOTbot - YouTube Over Telegram
HeyHo this is a Telegram Bot for downloading YouTube videos as MP3 Files.
It's running at [YOTBot](https://telegram.me/yotbot)
 
## Requirements
You have to install all packages mentioned in the requirements.txt.
```bash
pip install -r requirements.txt
```

## Environment Variables
You have to write the token you got from [BotFather](https://telegram.me/BotFather) into the environment variable TG_BOT_TOKEN.
```bash
export TG_BOT_TOKEN="969855739:AAEqhAK5peBt42I7Z4FqsOFxGQO818ja768"
```


## Run  
To start the bot execute the following command. Replace <NameOfMyTGBot> with the name of your bot. To customize the messages the bot writes, you need to modify responses.json, or rewrite it and pass it here.
```bash
python main.py myNewYTBot responses.json
```

## Licence
GPL 3

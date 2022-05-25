FROM python
WORKDIR /yotbot
COPY . /yotbot
RUN apt-get update
RUN apt-get install -y ffmpeg
RUN pip install -r requirements.txt
ENTRYPOINT ["python", "YOTBot.py"]

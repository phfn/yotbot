FROM python
RUN apt-get update
RUN apt-get install -y ffmpeg
WORKDIR /yotbot
COPY . /yotbot
RUN pip install -r requirements.txt
ENTRYPOINT ["python", "YOTBot.py"]

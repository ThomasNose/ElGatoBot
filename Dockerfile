FROM python:3.11.2

WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

COPY . .

RUN cd google-images-download && python3 setup.py install
RUN mkdir downloads
RUN apt-get update && apt-get install ffmpeg

CMDP["python3", "main.py"]
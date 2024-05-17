FROM python:3.9.16

WORKDIR /app
#COPY requirements.txt requirements.txt
#RUN pip install -r requirements.txt

COPY . /app

RUN pip install discord==2.3.2
RUN pip install numpy==1.26.4
RUN pip install openai==1.12.0
RUN pip install pandas==2.2.1
RUN pip install psycopg==3.1.18
RUN pip install psycopg-binary==3.1.18
RUN pip install requests==2.31.0
RUN pip install boto3
RUN pip install python-dotenv==1.0.1
RUN pip install yt_dlp
RUN pip install ffmpeg
RUN pip install PyNaCl

# Download ffmpeg archive
RUN curl -O https://johnvansickle.com/ffmpeg/releases/ffmpeg-release-amd64-static.tar.xz
RUN tar -xvf ffmpeg-release-amd64-static.tar.xz
RUN mv ffmpeg-*/ffmpeg /usr/local/bin/
RUN rm ffmpeg-release-amd64-static.tar.xz

CMD ["python3", "main.py"]

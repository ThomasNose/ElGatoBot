FROM python:3.9.16

WORKDIR /app
#COPY requirements.txt requirements.txt
#RUN pip install -r requirements.txt

COPY . /app

RUN pip install discord==2.3.2
#dotenv==0.0.5
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

CMD ["python3", "main.py"]

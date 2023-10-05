FROM python:3.11-bookworm

WORKDIR /usr/johnson/

COPY . .

RUN pip install -r requirements.txt 

# Install FFMPEG
RUN apt-get -y update
RUN apt-get install -y --fix-missing ffmpeg

CMD python3 coggers.py

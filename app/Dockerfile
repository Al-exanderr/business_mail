FROM python:3.8

ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE 1

RUN apt-get update
RUN apt-get install python3-pip -y
COPY ./requirements.txt requirements.txt
RUN pip install -r requirements.txt
RUN apt-get update
RUN apt-get install wkhtmltopdf -y
COPY ./entrypoint.sh entrypoint.sh
RUN chmod a+x entrypoint.sh

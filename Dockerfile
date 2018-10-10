FROM python:3.6

RUN mkdir /app
RUN mkdir /app/staticfiles

WORKDIR /app

ADD requirements.txt /app/

RUN pip install -r requirements.txt

ADD moviedb_rest_api moviedb_rest_api
ADD manage.py manage.py
ADD heroku_runserver.sh heroku_runserver.sh

USER www-data

CMD [ "bash", "heroku_runserver.sh" ]

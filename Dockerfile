 FROM python:3.6
 RUN mkdir /app
 WORKDIR /app
 ADD requirements.txt /app/
 RUN pip install -r requirements.txt
 ADD moviedb_rest_api moviedb_rest_api
 ADD manage.py manage.py
 
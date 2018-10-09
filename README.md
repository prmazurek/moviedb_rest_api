# Movie db REST API

A simple django rest api, created as a portfolio project.

## Development version
Create file called `docker-compose.override.yml` and paste this inside:
```
version: '3'

services:
  web:
    build:
      context: .
      dockerfile: Dockerfile.dev
```
This will override Dockerfile for your local build and install requirements-dev.txt as well as requirements.txt. 
Once that's done follow steps from next section.

### Installing

This project has been set up to work with docker. Before installing it make sure you have [Docker](https://docs.docker.com/install/) and [docker-compose](https://docs.docker.com/compose/install/) up and running.

You will need to request a free application secrate key on [OMDb API](http://www.omdbapi.com/apikey.aspx).
Create file called `.env` and paste `OMDB_SECRET='<your secret omdb key>'` inside.

Go to project root directory and execute following commands.

```
docker-compose build
docker-compose up
docker exec -it moviedb_rest_api_web python manage.py migrate
```

Once that's done you should be able to access 127.0.0.1:8000/

## Runnung tests
On development version do `docker exec -it moviedb_rest_api_web python manage.py test`

## How to use it
Let's go through a simple tutorial, everything should be clear after that.

1. Navigate to http://127.0.0.1:8000/movies/
Go ahead and paste `{"movie_title": "terminator"}` into 'Content' field and hit that Post button. This will create an object in db and return to you a terminator movie data. You can do that with movie title as many times as you wish.
Doing a GET request to '/movies/' page will return a list containing data of all movie objects currently in db.
2. Navigate to http://127.0.0.1:8000/comments/
This time paste in `{"movie_id": 1, "comment_body": "Lorem ipsum"}` and hit Post. This will create and a a comment to movie with id == 1. Again in the response you will get back a comment object data.
Now if you do refresh you will get back a list of all the comments. If you wish to to filter them by movie add a `movie_id=<id>` GET param. For example `comments/?movie_id=1`.
3. The last view is '/top/'. This View requires a date range to work properly. You can use an [online epoch conventer](https://www.epochconverter.com/) just add and substruct few hours from now. and use those timestamps in next url. Navigate to `http://127.0.0.1:8000/?date_from=<timestamp_from>&date_to=<timestamp_to>`. This view will return current ranking of movies based on the amounts of comments added to them.

## Built With

* [Django](https://docs.djangoproject.com/en/1.11/) - 1.11.16
* [Django Rest Framework](https://www.django-rest-framework.org/) - 3.8.2

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

Create file called `.env` and paste `OMDB_SECRET='<your secret key>'` inside.

Go to project root directory and execute following commands.

```
docker-compose build .
docker-compose up
docker exec -it netguru_web_1 python manage.py migrate
```

Once that's done you should be able to access 127.0.0.1:8000/

## Runnung tests
On development version do `docker exec -it netguru_web_1 python manage.py test`

## Built With

* [Django](https://docs.djangoproject.com/en/1.11/)
* [Django Rest Framework](https://www.django-rest-framework.org/)

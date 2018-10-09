import requests
import datetime

from django.conf import settings
from django.db.models import Count
from django.template.loader import render_to_string
from django.utils.html import mark_safe

from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView

from moviedb_rest_api.models import Movie, Comment
from moviedb_rest_api.serializers import MovieSerializer, CommentSerializer, TopMoviesSerializer


class MoviesView(APIView):

    def post(self, request):
        movie_title = request.data.get('movie_title')
        if not movie_title:
            return Response({}, status=status.HTTP_400_BAD_REQUEST)
        created, movie_data = self.get_movie_data(movie_title)
        return Response(movie_data, status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)

    def get(self, request):
        return Response(self.get_all_movies_serialized(), status=status.HTTP_200_OK)

    def get_view_description(self, html=False):
        description_data = {
            "POST": {
                "Accepted values": {
                    "movie_title": 'Required - string'
                },
                "description": "Finds and saves movie details to the db.",
                "Returns": "Dictionary containing movie data."
            },
            "GET": {
                "Accepted values": {},
                "description": "Retrieve movies records from db.",
                "Returns": "List of dictionaries containing movies data."
            }
        }
        if html:
            return mark_safe(render_to_string('view_description.html', {'description_data': description_data}))
        else:
            return description_data

    def omdb_url(self, movie_title):
        return '{host}?apikey={apikey}&t={movie_title}'.format(
            host=settings.OMDB_API_URL, apikey=settings.OMDB_API_KEY, movie_title=movie_title
        )

    def get_movie_data(self, movie_title):
        movie = Movie.objects.get_or_none(title__iexact=movie_title)
        if movie:
            return False, MovieSerializer(movie).data
        else:
            response = requests.get(self.omdb_url(movie_title))
            response_data = response.json()
            if response.status_code == status.HTTP_200_OK and not 'Error' in response_data:
                movie = Movie.objects.create(title=movie_title.title(), additional_data=response_data)
                return True, MovieSerializer(movie).data
            else:
                return False, {'OMDB_Error': response_data.get('Error')}

    @staticmethod
    def get_all_movies_serialized():
        movies = Movie.objects.all()
        return MovieSerializer(movies, many=True).data

class CommentsView(APIView):

    def post(self, request):
        try:
            movie_id = int(request.data.get('movie_id'))
        except (TypeError, ValueError):
            return Response({}, status=status.HTTP_400_BAD_REQUEST)
        else:
            comment_body = request.data.get('comment_body')
            comment = self.create_new_comment(movie_id, comment_body)
            if not comment:
                return Response({}, status=status.HTTP_400_BAD_REQUEST)
            return Response(comment, status=status.HTTP_201_CREATED)

    def get(self, request):
        movie_id = request.query_params.get('movie_id')
        if movie_id and not movie_id.isdigit():
            return Response([], status=status.HTTP_400_BAD_REQUEST)

        comments = self.get_serialized_comments(movie_id)
        return Response(comments, status=status.HTTP_200_OK)

    def get_view_description(self, html=False):
        description_data = {
            "POST": {
                "Accepted values": {
                    "movie_id": 'Required - integer',
                    "comment_body": 'Required - string'
                },
                "description": "Saves comment to given movie id.",
                "Returns": "Dictionary with saved comment data."
            },
            "GET": {
                "Accepted values": {
                    "movie_id": "integer"
                },
                "description": "Filters comments by movie id. "
                               "You will get all comments saved in the db if movie id is not specified.",
                "Returns": "List of dictionaries containing comments data."
            }
        }
        if html:
            return mark_safe(render_to_string('view_description.html', {'description_data': description_data}))
        else:
            return description_data

    @staticmethod
    def create_new_comment(movie_id, comment_body):
        if comment_body:
            movie = Movie.objects.get_or_none(id=movie_id)
            if movie:
                comment = Comment.objects.create(movie=movie, movie_id=movie_id, body=comment_body)
                return CommentSerializer(comment).data

    @staticmethod
    def get_serialized_comments(movie_id):
        filter_kwargs = {}
        if movie_id:
            filter_kwargs['movie_id'] = movie_id
        comments = Comment.objects.filter(**filter_kwargs)
        return CommentSerializer(comments, many=True).data


class TopMoviesView(APIView):
    def get(self, request):
        try:
            date_from = float(request.query_params.get('date_from'))
            date_from = datetime.datetime.utcfromtimestamp(date_from)
            date_to = float(request.query_params.get('date_to'))
            date_to = datetime.datetime.utcfromtimestamp(date_to)
        except (ValueError, TypeError):
            return Response([], status=status.HTTP_400_BAD_REQUEST)
        else:
            comments = self.get_top_comments(date_from, date_to)
            return Response(comments, status=status.HTTP_200_OK)

    def get_view_description(self, html=False):
        description_data = {
            "GET": {
                "Accepted values": {
                    "date_from": "Required - UTC timestamp",
                    "date_to": "Required - UTC timestamp"
                },
                "description": "Filters movies by date.",
                "Returns": "List of dictionaries containing movie id, number of comments and rank in the db."
            }
        }
        if html:
            return mark_safe(render_to_string('view_description.html', {'description_data': description_data}))
        else:
            return description_data

    @staticmethod
    def get_top_comments(date_from, date_to):
        movies = Movie.objects.filter(
            created_at__gte=date_from, created_at__lte=date_to
        ).annotate(comments_count=Count('comments')).order_by('-comments_count', 'id')
        return TopMoviesSerializer(movies, many=True).data

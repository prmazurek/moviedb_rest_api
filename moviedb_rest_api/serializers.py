from rest_framework import serializers

from moviedb_rest_api.models import Movie, Comment


class MovieSerializer(serializers.ModelSerializer):
    movie_id = serializers.IntegerField(source='id', read_only=True)

    class Meta:
        model = Movie
        fields = ('movie_id', 'title', 'additional_data', 'created_at')


class CommentSerializer(serializers.ModelSerializer):
    comment_id = serializers.IntegerField(source='id', read_only=True)
    movie_id = serializers.IntegerField(source='movie.id', read_only=True)

    class Meta:
        model = Comment
        fields = ('movie_id', 'comment_id', 'body', 'created_at')

class TopMoviesSerializer(serializers.ModelSerializer):
    comments_count = None
    movie_rank = 0

    movie_id = serializers.IntegerField(source='id', read_only=True)
    total_comments = serializers.IntegerField(source='comments_count', read_only=True)
    rank = serializers.SerializerMethodField()

    class Meta:
        model = Movie
        fields = ('movie_id', 'total_comments', 'rank')

    def get_rank(self, obj):
        if not self.comments_count or obj.comments_count < self.comments_count:
            self.comments_count = obj.comments_count
            self.movie_rank += 1
        return self.movie_rank

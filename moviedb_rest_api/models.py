from django.contrib.postgres.fields import JSONField
from django.db import models


class MovieManager(models.Manager):

    def get_or_none(self, **kwargs):
        try:
            movie = self.get(**kwargs)
        except self.model.DoesNotExist:
            movie = None
        finally:
            return movie


class Movie(models.Model):
    title = models.CharField(max_length=255, unique=True, blank=False, null=False)
    additional_data = JSONField()
    created_at = models.DateTimeField(auto_now_add=True)

    objects = MovieManager()


class Comment(models.Model):
    movie = models.ForeignKey(Movie, related_name='comments')
    body = models.TextField(null=False, blank=False)
    created_at = models.DateTimeField(auto_now_add=True)

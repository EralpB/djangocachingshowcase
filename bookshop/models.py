from django.db import models
from django.core.cache import cache
import time

class Author(models.Model):
    name = models.CharField(max_length=255)

    def get_top_books(self):
        cache_key = 'Author:get_top_books:{}'.format(self.id)
        cache_value = cache.get(cache_key)
        if cache_value is not None:
            return cache_value

        time.sleep(5)  # make the calculation slower for the sake of argument
        books = list(Book.objects.order_by('-purchase_count')[:10])
        cache.set(cache_key, books, 4 * 60 * 60)  # cache for 4 hours
        return books

    def __str__(self):
        return self.name


class Book(models.Model):
    title = models.CharField(max_length=255)
    author = models.ForeignKey(Author, on_delete=models.CASCADE)
    purchase_count = models.IntegerField()

    def __str__(self):
        return '{} by {}'.format(self.title, self.author)

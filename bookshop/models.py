from django.db import models
from django.core.cache import cache
import time
import redis

r = redis.Redis(host='localhost', port=6379, db=0)


class Author(models.Model):
    name = models.CharField(max_length=255)

    # _ indicates this function is for internal use only
    def _get_top_books(self):
        time.sleep(5)  # make the calculation slower for the sake of argument
        return list(Book.objects.order_by('-purchase_count')[:10])

    def get_top_books(self):
        cache_key = 'Author:get_top_books:{}'.format(self.id)
        lock_key = 'Lock:{}'.format(cache_key)
        cache_value = cache.get(cache_key)
        if cache_value is not None:
            return list(Book.objects.filter(id__in=cache_value))
        try:
            with r.lock(lock_key, timeout=60, blocking_timeout=0):
                books = self._get_top_books()
        except redis.exceptions.LockError:
            raise Exception('ColdCacheException')

        cache.set(cache_key, [book.id for book in books], 4 * 60 * 60)  # cache for 4 hours
        return books

    def __str__(self):
        return self.name


class Book(models.Model):
    title = models.CharField(max_length=255)
    author = models.ForeignKey(Author, on_delete=models.CASCADE)
    purchase_count = models.IntegerField()

    def __str__(self):
        return '{} by {}'.format(self.title, self.author)

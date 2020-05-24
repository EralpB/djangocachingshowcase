from django.db import models
from django.core.cache import cache
import time
import redis
import json

r = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)


class Author(models.Model):
    name = models.CharField(max_length=255)

    # _ indicates this function is for internal use only
    def _get_top_books(self):
        time.sleep(5)  # make the calculation slower for the sake of argument
        return list(Book.objects.order_by('-purchase_count')[:10])


    def get_top_books(self):
        CACHE_TIMEOUT = 24 * 60 * 60  # 1 day
        CACHE_FRESHNESS = 60 * 60  # 1 hour
        REMAINING_CUTOFF = CACHE_TIMEOUT - CACHE_FRESHNESS  # If TTL less than this value, needs recalculate

        cache_key = 'Author:get_top_books:{}'.format(self.id)
        lock_key = 'Lock:{}'.format(cache_key)
        cache_value = r.get(cache_key)
        if cache_value is not None:
            cache_value = json.loads(cache_value)
        remaining_ttl = r.ttl(cache_key)

        should_recalculate = remaining_ttl < REMAINING_CUTOFF

        if not should_recalculate and cache_value is not None:
            # if key is fresh enough, and value exists, just return!
            return list(Book.objects.filter(id__in=cache_value))

        # try to acquire lock to recalculate..
        try:
            with r.lock(lock_key, timeout=60, blocking_timeout=0):
                books = self._get_top_books()
        except redis.exceptions.LockError:
            # somebody else is calculating, if cache value exists, no problem, no error
            if cache_value is not None:
                return list(Book.objects.filter(id__in=cache_value))
            else:
                # we don't even have a stale cache, and some worker is calculating, no choice but to error out
                raise Exception('ColdCacheException')

        # only update the cache if you freshly calculated!
        # In other cases the execution doesnt reach here, it either gives exceptions or returns early.
        cache_representation = json.dumps([book.id for book in books])
        r.set(cache_key, cache_representation, CACHE_TIMEOUT)  # cache for 1 day
        return books

    def __str__(self):
        return self.name


class Book(models.Model):
    title = models.CharField(max_length=255)
    author = models.ForeignKey(Author, on_delete=models.CASCADE)
    purchase_count = models.IntegerField()

    def __str__(self):
        return '{} by {}'.format(self.title, self.author)

from django.db import models
import time

from functioncaching import cached_function


class Author(models.Model):
    name = models.CharField(max_length=255)

    @cached_function(timeout=24*60*60, freshness_timeout=60*60)
    def _get_top_book_ids(self):
        time.sleep(5)  # make the calculation slower for the sake of argument
        return list(Book.objects.filter(author=self).order_by('-purchase_count').values_list('id', flat=True)[:10])

    def get_top_books(self):
        return list(Book.objects.filter(id__in=self._get_top_book_ids()))

    def __str__(self):
        return self.name


class Book(models.Model):
    title = models.CharField(max_length=255)
    author = models.ForeignKey(Author, on_delete=models.CASCADE)
    purchase_count = models.IntegerField()

    def __str__(self):
        return '{} by {}'.format(self.title, self.author)

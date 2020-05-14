from django.db import models
import time

class Author(models.Model):
    name = models.CharField(max_length=255)

    def get_top_books(self):
        time.sleep(5)
        return list(Book.objects.filter(author=self).order_by('-purchase_count')[:10])

    def __str__(self):
        return self.name


class Book(models.Model):
    title = models.CharField(max_length=255)
    author = models.ForeignKey(Author, on_delete=models.CASCADE)
    purchase_count = models.IntegerField()

    def __str__(self):
        return '{} by {}'.format(self.title, self.author)

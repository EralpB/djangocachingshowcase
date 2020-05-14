import random
from django.core.management.base import BaseCommand
from bookshop.models import Author, Book

class Command(BaseCommand):
    help = 'Fills database with 1000 authors and 5000 books'

    def handle(self, *args, **options):
        for i in range(1000):
            Author.objects.create(name='Author {}'.format(i+1))

        author_count = Author.objects.count()
        for i in range(5000):
            author_id = random.randint(1, author_count-1)
            print(author_id)
            Book.objects.create(title='Book {}'.format(i+1),
                                author_id=author_id,
                                purchase_count=random.randint(0, 100))

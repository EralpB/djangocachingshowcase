import time
from django.shortcuts import render, get_object_or_404
from .models import Book, Author

def book_detail_view(request, pk):
    start_time = time.time()
    book = get_object_or_404(Book, pk=pk)
    authors_top_books = book.author.get_top_books()

    return render(request, 'bookshop/bookdetail.html', {
        'book': book,
        'authors_top_books': authors_top_books,
        'elapsedtime': time.time() - start_time
    })


def author_detail_view(request, pk):
    author = get_object_or_404(Author, pk=pk)
    return render(request, 'bookshop/authordetail.html', {
        'author': author,
    })


def index_view(request):
    authors = Author.objects.all()[:50]
    books = Book.objects.all()[:50]
    return render(request, 'bookshop/index.html', {
        'books': books,
        'authors': authors
    })

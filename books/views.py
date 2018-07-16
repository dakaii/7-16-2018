from django.db import transaction, IntegrityError
from django.contrib.auth.decorators import permission_required
from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.urls import reverse

import requests
from django.contrib.auth.decorators import login_required

from .models import Publisher, Author, Category, Book

GOOGLE_BOOK_API_URL = "https://www.googleapis.com/books/v1/volumes?q=isbn:{0}"


@login_required(login_url='/api/login/')
def search_books(request):
    isbn = request.GET.get('isbn', None)
    if isbn:
        book = Book.objects.filter(isbn_number=isbn).first()
        if book:
            book = {
                'isbn': book.isbn_number,
                'title': book.title,
                'authors': [author.name for author in book.authors.all()],
                'description': book.description,
                'publisher': book.publisher.name,
                'publication_date': book.publication_date,
                'categories': [category.category_tag for category in book.categories.all()],
                'thumbnail': book.thumbnail,
            }
        else:
            res = requests.get(GOOGLE_BOOK_API_URL.format(isbn))
            try:
                book = _parse_book_info(isbn, res)
                _save_to_db(book)
            except KeyError:
                book = {'error': 'No book with the provided ISBN number was found'}
        return render(request,
                      'books/book_details.html',
                      context={'book': book})
    else:
        return render(request, 'books/book_search.html')


def _parse_book_info(isbn, res):
    data = res.json()['items'][0]['volumeInfo']
    book = {
        'isbn': isbn,
        'title': data['title'],
        'authors': data['authors'],
        'description': data['description'],
        'publisher': data['publisher'],
        'publication_date': data['publishedDate'],
        'categories': data['categories'],
        'thumbnail': data['imageLinks']['thumbnail'],
        }
    return book


def _save_to_db(data):
    try:
        with transaction.atomic():
            book = Book.objects.create(isbn_number=data['isbn'],
                                       title=data['title'],
                                       description=data['description'],
                                       publication_date=data['publication_date'],
                                       thumbnail=data['thumbnail'],
                                       )
            for author_name in data['authors']:
                author = Author.objects.create(name=author_name)
                book.authors.add(author)

            for category_tag in data['categories']:
                category = Category.objects.create(category_tag=category_tag)
                book.categories.add(category)

            publisher = Publisher.objects.create(name=data['publisher'])
            book.publisher = publisher
            book.save()

    except IntegrityError as e:
        # TODO this should be replaced by a logger.
        print(e)

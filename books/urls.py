from django.urls import path

from . import registration, views

urlpatterns = [
    path('signup/', registration.SignUp.as_view()),
    path('books/', views.search_books),
]

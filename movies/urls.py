from django.urls import path
from . import views

urlpatterns = [
    path('<movie_id>', views.movie_details, name="movie-details"),
    path('', views.add_movies)
]
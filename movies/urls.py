from django.urls import path
from . import views

urlpatterns = [
    path('<movie_id>', views.movie_details),
    path('', views.add_movies)
]
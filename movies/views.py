from django.shortcuts import render, get_list_or_404, redirect
from django.http import HttpResponse
from .models import Movie, Language, Genre, Cast

import tmdbsimple as tmdb
from django.utils.dateparse import parse_date
import os
from tempfile import NamedTemporaryFile
from urllib.request import urlopen
from django.core.files import File

tmdb.API_KEY = '0a1eb75d23905284398cf65a74bcb87c'
POSTER_URL = 'https://image.tmdb.org/t/p/original'


# Create your views here.
def index(request):
    top_movies = Movie.objects.all().order_by('-overall_rating')
    top_action_movies = Movie.objects.filter(genres__name='Action').order_by('-overall_rating')
    top_thriller_movies = Movie.objects.filter(genres__name='Thriller')
    return render(request, 'movies/index.html', {'top_movies': top_movies, 'top_action_movies': top_action_movies, 'top_thriller_movies': top_thriller_movies})


def movie_details(request, movie_id):
    movie = get_list_or_404(Movie, api_identifier=movie_id)[0]
    image_url = 'http://' + request.get_host() + '/media/' + str(movie.poster)
    return render(request, 'movies/movie-details.html', {
        'title': movie.title,
        'description': movie.description,
        'year': movie.released_date.year,
        'poster': image_url
    })


def add_movies(request):
    print("Started adding movies")
    genre_mapping = {
        28: 1,
        12: 2,
        16: 3,
        35: 4,
        80: 5,
        99: 6,
        18: 7,
        10751: 8,
        14: 9,
        36: 10,
        27: 11,
        10402: 12,
        9648: 13,
        10749: 14,
        878: 15,
        10752: 16,
        53: 17,
        37: 18,
        10770: 19
    }
    list_of_movies = []

    years = [2017, 2018, 2019, 2020, 2021, 2022]
    discover = tmdb.Discover()
    for year in years:
        movies = discover.movie(
            language='en-US',
            sort_by='popularity.desc',
            year=year
        )
        for m in movies['results']:
            if m['original_language'] == 'en':
                list_of_movies.append(m['id'])

    unique_movie_list = set(list_of_movies)

    for identifier in unique_movie_list:
        movie_detail = tmdb.Movies(identifier).info()
        language = Language.objects.get(id=2)
        credit = tmdb.Movies(identifier).credits()
        cast_list = []

        for actor in credit['cast'][:5]:
            cast = Cast.objects.get_or_create(name=actor['name'])
            cast_list.append(cast[0])

        movie = Movie(
            title=movie_detail['title'],
            description=movie_detail['overview'],
            language=language,
            released_date=parse_date(movie_detail['release_date']),
            runtime=movie_detail['runtime'],
            overall_rating=movie_detail['vote_average']/2,
        )
        movie.save()
        movie.cast.add(*cast_list)
        movie.save()
        genre_obj = []
        for i in movie_detail['genres']:
            genre_obj.append(Genre.objects.get(id=genre_mapping[i['id']]))

        movie.genres.add(*genre_obj)
        movie.save()
        poster_temp = NamedTemporaryFile(delete=True)
        poster_temp.write(urlopen(POSTER_URL + movie_detail['poster_path']).read())
        poster_temp.flush()
        movie.poster.save(os.path.basename(POSTER_URL + movie_detail['poster_path']), File(poster_temp))

    print("Success")
    return HttpResponse("Added Successfully")

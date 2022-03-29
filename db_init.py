import django
import os
from tempfile import NamedTemporaryFile
from urllib.request import urlopen

import tmdbsimple as tmdb
from django.conf import settings
from django.core.files import File
from django.utils.dateparse import parse_date

from movies.models import Movie, Genre

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "movies_info.settings")
django.setup()
settings.configure()

tmdb.API_KEY = '0a1eb75d23905284398cf65a74bcb87c'
POSTER_URL = 'https://image.tmdb.org/t/p/original'


def init_genres():
    genre_list = tmdb.Genres().movie_list()
    for genre in genre_list['genres']:
        genre = Genre(id=genre['id'], name=genre['name'])
        genre.save()


def init_movies():
    #years = [2005, 2006, 2007, 2008, 2009, 2010, 2011, 2012, 2013, 2014, 2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022]
    discover = tmdb.Discover()
    for year in years:
        movies = discover.movie(
            language='en-US',
            sort_by='popularity.desc',
            year=year
        )

        for m in movies['results']:
            movie = Movie(
                api_identifier=m['id'],
                title=m['original_title'],
                description=m['overview'],
                language=m['original_language'],
                released_date=parse_date(m['release_date']),
                vote_count=m['vote_count'],
                vote_average=m['vote_average']
            )
            movie_info = tmdb.Movies(m['id']).info()
            movie.runtime = movie_info['runtime']
            genre_obj = []
            for i in movie_info['genres']:
                genre_obj.append(Genre.objects.get(id=i['id']))
            movie.save()
            movie.genres.add(*genre_obj)
            movie.save()
            poster_temp = NamedTemporaryFile(delete=True)
            poster_temp.write(urlopen(POSTER_URL + m['poster_path']).read())
            poster_temp.flush()
            movie.poster.save(os.path.basename(POSTER_URL + m['poster_path']), File(poster_temp))

            banner_temp = NamedTemporaryFile(delete=True)
            banner_temp.write(urlopen(POSTER_URL + m['backdrop_path']).read())
            banner_temp.flush()
            movie.banner.save(os.path.basename(POSTER_URL + m['backdrop_path']), File(banner_temp))



add_movies()

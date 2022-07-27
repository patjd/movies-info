import decimal
import random
import string
from itertools import islice
from textwrap import fill

from django.contrib.auth.models import User
from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from django.contrib.auth import authenticate, login, logout
from django.template.loader import render_to_string
from django.views import View

from .models import Movie, Language, Genre, Cast, Client, Rating, Order
from .forms import ProfileForm, OrderForm, SignUpForm

import tmdbsimple as tmdb
from django.utils.dateparse import parse_date
import os
from tempfile import NamedTemporaryFile
from urllib.request import urlopen
from django.core.files import File

from django.core.mail import send_mail, EmailMultiAlternatives
from django.utils.html import strip_tags
from django.conf import settings

tmdb.API_KEY = settings.TMDB_API_KEY
POSTER_URL = 'https://image.tmdb.org/t/p/original'


# Create your views here.
class IndexView(View):

    def get(self, request):
        top_movies = Movie.objects.all().order_by('-overall_rating')
        top_action_movies = Movie.objects.filter(genres__name='Action').order_by('-overall_rating')
        top_thriller_movies = Movie.objects.filter(genres__name='Drama').order_by('-overall_rating')
        context = {
            'top_movies': top_movies,
            'top_action_movies': top_action_movies,
            'top_thriller_movies': top_thriller_movies
        }
        if request.user.is_authenticated:
            client = Client.objects.get(username=request.user.username)
            context['profile'] = client
            print(client.watchlist.all())
        return render(request, 'movies/index.html', context)


def signup(request):
    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            form = form.save(commit=False)
            form.set_password(form.password)
            form.save()
            return render(request, 'movies/login.html')
        else:
            print(form.errors)
            return render(request, 'movies/sign-up.html', {'form': form})

    filled_form = SignUpForm()
    return render(request, 'movies/sign-up.html', {'fill_form': filled_form})


def signin(request):
    return render(request, 'movies/login.html')


def change_password(request):
    if request.method == 'POST':
        oldpassword = request.POST['oldpassword']
        newpassword = request.POST['newpassword']
        client = Client.objects.get(username=request.user.username)
        if client.check_password(oldpassword):
            client.set_password(newpassword)
            client.save()
            user = authenticate(username=client.username, password=newpassword)
            login(request, user)
            email_content = render_to_string('movies/includes/email-changed-password.html')
            text_content = strip_tags(email_content)
            send_mail('OMDb - Password Change', text_content, settings.EMAIL_HOST_USER,
                      [client.email])
            return render(request, 'movies/profile.html', {'profile': client})
        else:
            return render(request, 'movies/change-password.html', {'errors': True})
    else:
        return render(request, 'movies/change-password.html')


def auth(request):
    user = authenticate(username=request.POST['username'], password=request.POST['password'])
    if user is not None:
        login(request, user)
        return redirect('index')
    else:
        return render(request, 'movies/login.html', {'errors': True})


def signout(request):
    logout(request)
    return redirect('index')


def forgot_password(request):
    if request.method == 'POST':
        username = request.POST['username']
        try:
            client = Client.objects.get(username=username)
        except Client.DoesNotExist:
            return render(request, 'movies/forgot-password.html', {'errors': True})

        characters = string.ascii_letters + string.digits + string.punctuation
        password = ''.join(random.choice(characters) for i in range(8))
        client.set_password(password)
        client.save()
        send_mail('Movies Info - Forgot Password', 'Your new password is ' + password, settings.EMAIL_HOST_USER,
                  [client.email])
        return render(request, 'movies/login.html', {'forgot_password': True})
    else:
        return render(request, 'movies/forgot-password.html')


def search(request):
    search_term = request.POST['search']
    movies = Movie.objects.filter(title__contains=search_term)
    return render(request, 'movies/search-results.html', {'movies': movies})


def add_to_cart(request, movie_id):
    if request.user.is_authenticated:
        movie = Movie.objects.get(id=movie_id)
        client = Client.objects.get(username=request.user.username)
        client.cart.add(movie)
        return redirect('cart')
    else:
        return render(request, "movies/login.html")


def shopping_cart(request):
    client = Client.objects.get(username=request.user.username)
    total = 0
    for item in client.cart.all():
        total += item.price
    return render(request, 'movies/shopping-cart.html', {'movies': client.cart.all(), 'total': total})


def order_history(request):
    client = Client.objects.get(username=request.user.username)
    orders = Order.objects.filter(client__username=client.username).order_by('-order_date')
    return render(request, 'movies/order-history.html', {'orders': orders})


def remove_from_cart(request, movie_id):
    movie = Movie.objects.get(id=movie_id)
    client = Client.objects.get(username=request.user.username)
    client.cart.remove(movie)
    client.save()
    return redirect('cart')


def cast(request, cast_id):
    cast_detail = Cast.objects.get(id=cast_id)
    birthday = parse_date(cast_detail.birthday)
    return render(request, 'movies/cast.html', {'cast': cast_detail, 'birthday': birthday})


def watchlist(request):
    client = Client.objects.get(username=request.user.username)
    return render(request, 'movies/watchlist.html', {'movies': client.watchlist.all(), 'name': client.first_name})


def profile(request):
    client = Client.objects.get(username=request.user.username)
    return render(request, 'movies/profile.html', {'profile': client})


def place_order(request):
    client = Client.objects.get(username=request.user.username)
    print('Client', client)
    if request.method == 'POST':
        filled_form = OrderForm(request.POST)

        total = 0
        for movie in client.cart.all():
            total += movie.price

        if filled_form.is_valid():
            print('IN', client.cart.all())
            filled_form = filled_form.save(commit=False)
            filled_form.client = client
            filled_form.total_price = total
            filled_form.save()
            filled_form.movies.set(client.cart.all())
            filled_form.save()
            client.cart.clear()
            client.save()
            order_movies = [movie.title for movie in filled_form.movies.all()]
            html_content = render_to_string('movies/includes/email-order.html', {'order': filled_form, 'movies': order_movies})
            text_content = strip_tags(html_content)
            #send_mail('Order', text_content, settings.EMAIL_HOST_USER,[settings.RECIPIENT_ADDRESS])
            msg = EmailMultiAlternatives('Order', text_content, settings.EMAIL_HOST_USER, [client.email])
            msg.attach_alternative(html_content, "text/html")
            msg.send()
            return render(request, 'movies/placed-order.html', {'order': filled_form})
    else:
        fill_form = OrderForm(initial={'first_name':'', 'last_name':'', 'email':''})
        return render(request, 'movies/place-order.html', {'fill_form': fill_form})


def edit_user_details(request):
    client = Client.objects.get(username=request.user.username)
    if request.method == 'POST':
        filled_form = ProfileForm(request.POST)
        if filled_form.is_valid():
            client.first_name = filled_form.cleaned_data['first_name']
            client.last_name = filled_form.cleaned_data['last_name']
            client.email = filled_form.cleaned_data['email']
            client.password = filled_form.cleaned_data['password']
            client.address = filled_form.cleaned_data['address']
            client.save()
            return HttpResponse('Updated Successfully')
        else:
            print(filled_form.cleaned_data['first_name'])
            client = Client.objects.get(username=filled_form.cleaned_data['email'])

            client.save()
            return HttpResponse('Done')
    else:
        client = Client.objects.get(username=request.user.username)
        fill_form = ProfileForm({
            'username': client.username,
            'first_name': client.first_name,
            'last_name': client.last_name,
            'email': client.email,
            'password': client.password
        })
        fill_form.username = client.username
        fill_form.first_name = client.first_name
        fill_form.last_name = client.last_name
        return render(request, 'movies/edit-profile.html', {'fill_form': fill_form})


def remove_from_watchlist(request, movie_id):
    movie = Movie.objects.get(id=movie_id)
    client = Client.objects.get(username=request.user.username)
    client.watchlist.remove(movie)
    client.save()
    return redirect('watchlist')


def add_to_watchlist(request, movie_id):
    movie = Movie.objects.get(id=movie_id)
    client = Client.objects.get(username=request.user.username)
    client.watchlist.add(movie)
    client.save()
    return redirect('index')


class MovieDetailsView(View):

    def get(self, request, *args, **kwargs):
        movie = get_object_or_404(Movie, id=kwargs['movie_id'])
        rate=0
        incart=False
        if request.user.username:
            client = Client.objects.get(username=request.user.username)
            rating = Rating.objects.filter(movie=movie).filter(client=client)
            if movie in client.cart.all():
                incart = True
            else:
                incart = False
        else:
            rating = []


        image_url = 'http://' + request.get_host() + '/media/' + str(movie.poster)
        genres = [genre.name for genre in movie.genres.all()]



        if len(rating) != 0:
            rate = rating[0].rating
        else:
            rate = 0
        context = {
            'movie_id': kwargs['movie_id'],
            'title': movie.title,
            'description': movie.description,
            'year': movie.released_date.year,
            'release_date': movie.released_date,
            'poster': image_url,
            'genre': genres,
            'runtime': movie.runtime,
            'banner': movie.banner,
            'rating': rate,
            'overall_rating': movie.overall_rating,
            'cast': movie.cast.all(),
            'price': movie.price,
            'cart': incart
        }
        return render(request, 'movies/movie-info.html', context)


def rate_movie(request, movie_id):
    print(request.POST['rating'])
    user_rating = request.POST['rating']
    client = Client.objects.get(username=request.user.username)
    movie = Movie.objects.get(id=movie_id)
    updated_rating = (movie.overall_rating * movie.vote_count + decimal.Decimal(float(user_rating))) / (
            movie.vote_count + 1)
    movie.overall_rating = updated_rating
    movie.vote_count = movie.vote_count + 1
    movie.save()
    rating = Rating.objects.filter(movie=movie).filter(client=client)
    if len(rating) == 0:
        new_rating = Rating(
            rating=user_rating,
            movie=movie,
            client=client
        )
        new_rating.save()
    else:
        rating[0].rating = user_rating
        rating[0].save()
    return redirect('movie-details', movie_id=movie_id)


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

    years = [2000, 2001, 2002, 2003, 2004, 2005, 2006, 2007, 2008, 2009, 2010, 2011, 2012, 2013, 2014, 2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022]
    discover = tmdb.Discover()
    print(discover)
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
            people = tmdb.People(actor['id']).info()
            image = ''
            birthday = ''
            bio = ''
            if isinstance(people['birthday'], str):
                birthday = people['birthday']
            if isinstance(people['profile_path'], str):
                image = 'https://image.tmdb.org/t/p/original' + people['profile_path']
            if isinstance(people['biography'], str):
                bio = people['biography']

            cast = Cast.objects.get_or_create(name=people['name'], bio=bio, birthday=birthday, image=image)

            cast_list.append(cast[0])

        if movie_detail['backdrop_path'] is not None:
            banner = 'https://image.tmdb.org/t/p/original' + movie_detail['backdrop_path']
        else:
            banner = ''
        movie = Movie(
            title=movie_detail['title'],
            description=movie_detail['overview'],
            language=language,
            released_date=parse_date(movie_detail['release_date']),
            runtime=movie_detail['runtime'],
            overall_rating=movie_detail['vote_average'] / 2,
            banner=banner,
            vote_count=movie_detail['vote_count']
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

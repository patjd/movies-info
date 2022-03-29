from django.contrib.auth.models import User
from django.db import models


# Create your models here.

class Genre(models.Model):
    name = models.CharField(max_length=20)

    def __str__(self):
        return str(self.id) + ' ' + self.name


class Cast(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name


class Language(models.Model):
    name = models.CharField(max_length=20)

    def __str__(self):
        return self.name


class Movie(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField(max_length=1000)
    poster = models.ImageField(upload_to='poster')
    genres = models.ManyToManyField(Genre)
    language = models.ForeignKey(Language, on_delete=models.SET_NULL, null=True)
    cast = models.ManyToManyField(Cast)
    released_date = models.DateField()
    runtime = models.PositiveIntegerField()
    overall_rating = models.DecimalField(max_digits=2, decimal_places=1, default=0)
    price = models.DecimalField(max_digits=5, decimal_places=2, default=10)

    def __str__(self):
        return self.title


class Client(User):
    address = models.TextField(max_length=1000)
    watchlist = models.ManyToManyField(Movie, related_name='watchlist', blank=True)
    cart = models.ManyToManyField(Movie, related_name='cart', blank=True)

    def __str__(self):
        return self.username


class Rating(models.Model):
    rating = models.DecimalField(max_digits=2, decimal_places=1)
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)
    client = models.ForeignKey(Client, on_delete=models.CASCADE)


class Order(models.Model):
    shipping_address = models.TextField(max_length=1000)
    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    movies = models.ManyToManyField(Movie)
    total_price = models.DecimalField(max_digits=6, decimal_places=2)

    def __str__(self):
        return str(self.id) + ' ' + self.client.username

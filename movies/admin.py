from django.contrib import admin
from .models import Genre, Movie, Cast, Language, Client, Rating, Order

# Register your models here.
admin.site.register(Genre)
admin.site.register(Movie)
admin.site.register(Cast)
admin.site.register(Language)
admin.site.register(Client)
admin.site.register(Rating)
admin.site.register(Order)

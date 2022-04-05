from django.urls import path
from . import views

urlpatterns = [
    path('change-password', views.change_password, name='change-password'),
    path('cast/<cast_id>', views.cast, name='cast'),
    path('search', views.search, name='search'),
    path('forgot-password', views.forgot_password, name='forgot-password'),
    path('order-history', views.order_history, name='order-history'),
    path('place-order', views.place_order, name="place-order"),
    path('edit-profile', views.edit_user_details, name="edit-profile"),
    path('auth', views.auth, name="auth"),
    path('profile', views.profile, name="profile"),
    path('shopping-cart', views.shopping_cart, name="cart"),
    path('add-to-cart/<movie_id>', views.add_to_cart, name="shopping-cart"),
    path('remove-from-cart/<movie_id>', views.remove_from_cart, name="remove-cart"),
    path('watchlist', views.watchlist, name="watchlist"),
    path('add-to-watchlist/<movie_id>', views.add_to_watchlist, name="add-watchlist"),
    path('remove-from-watchlist/<movie_id>', views.remove_from_watchlist, name="remove-watchlist"),
    path('rate/<movie_id>', views.rate_movie, name="rating"),
    path('signup', views.signup, name="signup"),
    path('signin', views.signin, name="signin"),
    path('signout', views.signout, name="signout"),
    path('<movie_id>', views.MovieDetailsView.as_view(), name="movie-details"),
    path('', views.add_movies)
]
from django.urls import path
from . import views

urlpatterns = [
    path("", views.movie_list, name="list"),
    path("watchlist/", views.watchlist, name="watchlist"),
    path("movie/<slug:slug>/", views.movie_detail, name="detail"),
    path("movie/<slug:slug>/watchlist", views.toggle_watchlist, name="toggle_watchlist"),
    path("movie/<slug:slug>/review/delete", views.delete_review, name="delete_review"),
]
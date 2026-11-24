from django.contrib import admin
from django.urls import path, include
from restaurant import views as restaurant_views

urlpatterns = [
    path(
        '',
        restaurant_views.landing,
        name='landing'
    ),

    path(
        'restaurant/',
        include('restaurant.urls')
    ),

    path(
        'ngo/',
        include('ngo.urls')
    ),

    path(
        'admin/',
        admin.site.urls
    ),
    path(
        "forecast/",
        include("forecasting.urls")
    ),
]
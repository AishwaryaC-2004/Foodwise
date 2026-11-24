from django.urls import path
from . import views

urlpatterns = [

    path(
        'login/',
        views.login_view,
        name='login'
    ),

    path(
        'dashboard/',
        views.dashboard,
        name='dashboard'
    ),

    path(
        'forecast/',
        views.prediction,
        name='prediction'
    ),

    path(
        'production/',
        views.production,
        name='production'
    ),
    path(
        'logout/',
        views.logout_view,
        name='logout'
    ),
    path(
        'donations/',
        views.donations,
        name='donations'
    ),
    path(
        'simulator/',
        views.simulator,
        name='simulator'
    ),
    path(
        'map/',
        views.map_view,
        name='map'
    ),
    path(
        'analytics/',
        views.analytics,
        name='analytics'
    ),
]
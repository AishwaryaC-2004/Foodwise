from django.urls import path
from . import views

urlpatterns = [

    path(
        '',
        views.ngo_login,
        name='ngo_login'
    ),

    path(
        'dashboard/',
        views.ngo_dashboard,
        name='ngo_dashboard'
    ),

    path(
        'requirements/',
        views.requirements,
        name='requirements'
    ),

    path(
        'match/',
        views.run_matching_view,
        name='run_matching'
    ),
    path(
        'accept/<int:match_id>/',
        views.accept_match,
        name='accept_match'
    ),
    path(
        'reject/<int:match_id>/',
        views.reject_match,
        name='reject_match'
    ),
    path(
    "generate/",
    views.generate_matches,
    name="generate_matches"
),
]
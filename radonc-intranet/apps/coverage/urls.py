from django.urls import path

from . import views

app_name = "coverage"

urlpatterns = [
    path("", views.coverage_home, name="home"),
    path("matrix/", views.coverage_matrix, name="matrix"),
]

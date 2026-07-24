from django.urls import path

from . import views

app_name = "huddle"

urlpatterns = [
    path("", views.huddle_board, name="board"),
]

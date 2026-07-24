from django.urls import path

from . import views

app_name = "linkhub"

urlpatterns = [
    path("", views.link_hub, name="hub"),
]

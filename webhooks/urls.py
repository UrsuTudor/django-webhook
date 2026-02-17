from django.urls import path

from . import views

app_name = "webhooks"

urlpatterns = [
  path("webhooks/<str:service>/", views.receiver, name="receiver")
]

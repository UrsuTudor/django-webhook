from django.urls import path

from . import views

app_name = "webhooks"

urlpatterns = [
  path("send", views.receiver, name="receiver")
]

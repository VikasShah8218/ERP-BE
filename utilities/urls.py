from django.urls import path
from .views import *
from . import views

urlpatterns = [
    path('test/',test.as_view()),
]
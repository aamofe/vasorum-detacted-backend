from django.urls import path
from .views import *
urlpatterns = [
    path('login',login),
    path('register',register),
    path('get_info',get_info),
    path('upload_avatar',upload_avatar)
]
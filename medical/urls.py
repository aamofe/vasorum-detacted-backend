from django.urls import path

from backend import settings
from .views import *
from medical import views
urlpatterns = [
    path('upload',upload),
    path('test',test),
    path('get_ct',get_ct),
    path("get_case",get_case),
    path("add_patient",add_patient),
    path("delete_patient",delete_patient),
    path("get_patient",get_patient),
    path("get_all_patient",get_all_patient),
    path("update_patient",update_patient)
]
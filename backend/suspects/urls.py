from django.urls import path
from .views import MostWantedList

urlpatterns = [
    path("most-wanted/", MostWantedList.as_view(), name="most_wanted"),
]

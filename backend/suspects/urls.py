from django.urls import path

from .views import MostWantedList, CaseSuspects, SuspectUpdate

urlpatterns = [
    path("most-wanted/", MostWantedList.as_view(), name="most_wanted"),
    path("case/<int:case_id>/", CaseSuspects.as_view(), name="case_suspects"),
    path("<int:suspect_id>/", SuspectUpdate.as_view(), name="suspect_update"),
]

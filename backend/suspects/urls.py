from django.urls import path

from .views import MostWantedList, CaseSuspects, SuspectRankUpdate

urlpatterns = [
    path("most-wanted/", MostWantedList.as_view(), name="most_wanted"),
    path("case/<int:case_id>/", CaseSuspects.as_view(), name="case_suspects"),
    path("<int:suspect_id>/rank/", SuspectRankUpdate.as_view(), name="suspect_rank_update"),
]

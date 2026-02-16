from django.urls import path

from .views import SubmitTip, OfficerReviewTip, DetectiveApproveTip, RewardLookup

urlpatterns = [
    path("tips/submit/", SubmitTip.as_view(), name="tip_submit"),
    path("tips/<int:tip_id>/officer-review/", OfficerReviewTip.as_view(), name="tip_officer_review"),
    path("tips/<int:tip_id>/detective-approve/", DetectiveApproveTip.as_view(), name="tip_detective_approve"),
    path("lookup/", RewardLookup.as_view(), name="reward_lookup"),
]

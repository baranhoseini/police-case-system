from django.urls import path
from .views import RolesListView, AssignRoleView

urlpatterns = [
    path("roles/", RolesListView.as_view(), name="roles_list"),
    path("assign-role/", AssignRoleView.as_view(), name="assign_role"),
]

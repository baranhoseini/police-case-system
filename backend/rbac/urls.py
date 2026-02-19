from django.urls import path
from rbac.views import (
    RolesListCreateView,
    RoleDetailView,
    AssignRoleView,
    RevokeRoleView,
    MyRolesView,
)

urlpatterns = [
    path("roles/", RolesListCreateView.as_view(), name="roles-list-create"),
    path("roles/<int:role_id>/", RoleDetailView.as_view(), name="role-detail"),
    path("assign-role/", AssignRoleView.as_view(), name="assign-role"),
    path("revoke-role/", RevokeRoleView.as_view(), name="revoke-role"),
    path("me/roles/", MyRolesView.as_view(), name="my-roles"),
]

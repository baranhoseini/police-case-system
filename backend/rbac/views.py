from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from rbac.models import Role, UserRole
from rbac.permissions import HasRole
from rbac.serializers import (
    RoleSerializer,
    RoleCreateUpdateSerializer,
    AssignRoleSerializer,
    RevokeRoleSerializer,
)


class AssignRoleView(APIView):
    permission_classes = [HasRole.with_roles("Admin")]

    def post(self, request):
        serializer = AssignRoleSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"detail": "Role assigned"}, status=status.HTTP_201_CREATED)


class RolesListCreateView(APIView):
    permission_classes = [HasRole.with_roles("Admin")]

    def get(self, request):
        roles = Role.objects.all().order_by("name")
        return Response(RoleSerializer(roles, many=True).data)

    def post(self, request):
        serializer = RoleCreateUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        role = serializer.save()
        return Response(RoleSerializer(role).data, status=status.HTTP_201_CREATED)


class RoleDetailView(APIView):
    permission_classes = [HasRole.with_roles("Admin")]

    def patch(self, request, role_id):
        role = Role.objects.filter(id=role_id).first()
        if not role:
            return Response({"detail": "Role not found"}, status=status.HTTP_404_NOT_FOUND)

        serializer = RoleCreateUpdateSerializer(role, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        role = serializer.save()
        return Response(RoleSerializer(role).data)

    def delete(self, request, role_id):
        role = Role.objects.filter(id=role_id).first()
        if not role:
            return Response({"detail": "Role not found"}, status=status.HTTP_404_NOT_FOUND)

        if UserRole.objects.filter(role=role).exists():
            return Response(
                {"detail": "Role is assigned to users; revoke first"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        role.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)




class RevokeRoleView(APIView):
    permission_classes = [HasRole.with_roles("Admin")]

    def post(self, request):
        serializer = RevokeRoleSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"detail": "Role revoked"}, status=status.HTTP_200_OK)


class MyRolesView(APIView):
    def get(self, request):
        if not request.user or not request.user.is_authenticated:
            return Response({"detail": "Authentication required"}, status=status.HTTP_401_UNAUTHORIZED)

        roles = Role.objects.filter(userrole__user=request.user).order_by("name")
        return Response(RoleSerializer(roles, many=True).data)

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from rbac.models import Role
from rbac.permissions import HasRole
from rbac.serializers import RoleSerializer, AssignRoleSerializer

class RolesListView(APIView):
    permission_classes = [HasRole.with_roles("Admin")]

    def get(self, request):
        roles = Role.objects.all().order_by("name")
        return Response(RoleSerializer(roles, many=True).data)

class AssignRoleView(APIView):
    permission_classes = [HasRole.with_roles("Admin")]

    def post(self, request):
        serializer = AssignRoleSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"detail": "Role assigned"}, status=status.HTTP_201_CREATED)

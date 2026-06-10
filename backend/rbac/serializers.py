from django.contrib.auth import get_user_model
from rest_framework import serializers
from rbac.models import Role, UserRole
from rbac.permissions import canonicalize_role_name, expand_role_names


User = get_user_model()

def _resolve_role_by_name(name: str) -> Role:
    # 1) exact
    role = Role.objects.filter(name=name).first()
    if role:
        return role

    # 2) canonical (document name)
    canonical = canonicalize_role_name(name)
    role = Role.objects.filter(name=canonical).first()
    if role:
        return role

    # 3) try any alias spellings for this canonical role
    for candidate in expand_role_names(name):
        role = Role.objects.filter(name=candidate).first()
        if role:
            return role

    raise Role.DoesNotExist

class RoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Role
        fields = ("id", "name", "description")

class AssignRoleSerializer(serializers.Serializer):
    user_id = serializers.IntegerField()
    role_name = serializers.CharField()

    def validate(self, attrs):
        user_id = attrs["user_id"]
        role_name = attrs["role_name"]

        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            raise serializers.ValidationError({"user_id": "User not found"})

        try:
            role = _resolve_role_by_name(role_name)
        except Role.DoesNotExist:
            raise serializers.ValidationError({"role_name": "Role not found"})

        attrs["user"] = user
        attrs["role"] = role
        return attrs

    def create(self, validated_data):
        obj, _ = UserRole.objects.get_or_create(
            user=validated_data["user"],
            role=validated_data["role"],
        )
        return obj


class RoleCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Role
        fields = ("name", "description")


class RevokeRoleSerializer(serializers.Serializer):
    user_id = serializers.IntegerField()
    role_name = serializers.CharField()

    def validate(self, attrs):
        try:
            user = User.objects.get(id=attrs["user_id"])
        except User.DoesNotExist:
            raise serializers.ValidationError({"user_id": "User not found"})

        try:
            role = _resolve_role_by_name(attrs["role_name"])
        except Role.DoesNotExist:
            raise serializers.ValidationError({"role_name": "Role not found"})

        attrs["user"] = user
        attrs["role"] = role
        return attrs

    def save(self, **kwargs):
        UserRole.objects.filter(user=self.validated_data["user"], role=self.validated_data["role"]).delete()
        return True

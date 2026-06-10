from django.contrib.auth import get_user_model
from django.db.models import Q
from rest_framework import serializers
from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.tokens import RefreshToken

from django.contrib.auth import get_user_model
from rest_framework import serializers
from rbac.models import Role, UserRole
from rbac.permissions import canonicalize_role_name



User = get_user_model()

class UserPublicWithRolesSerializer(serializers.ModelSerializer):
    roles = serializers.SerializerMethodField()
    primary_role = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            "id", "username", "first_name", "last_name",
            "email", "phone", "national_id",
            "roles", "primary_role",
        )

    def get_roles(self, obj):
        raw = list(
            UserRole.objects.filter(user=obj)
            .select_related("role")
            .values_list("role__name", flat=True)
        )
        # Return document-canonical role names (stable for frontend)
        canon = [canonicalize_role_name(r) for r in raw]
        # de-duplicate preserving order
        out = []
        seen = set()
        for r in canon:
            if r not in seen:
                seen.add(r)
                out.append(r)
        return out

    def get_primary_role(self, obj):
        roles = self.get_roles(obj)
        priority = ["Administrator","Chief","Captain","Sergent","Detective","Police Officer","Patrol Officer","Cadet","Judge","Corenary","Base user","Complainant","Witness","Suspect","Criminal"]
        for r in priority:
            if r in roles:
                return r
        return roles[0] if roles else None





class UserPublicSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("id", "username", "first_name", "last_name", "email", "phone", "national_id")



class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = User
        fields = (
            "username",
            "password",
            "email",
            "phone",
            "first_name",
            "last_name",
            "national_id",
        )

    def validate(self, attrs):
        # strip whitespace
        for f in ("username", "email", "phone", "first_name", "last_name", "national_id"):
            attrs[f] = (attrs.get(f) or "").strip()

        required = ("username", "email", "phone", "first_name", "last_name", "national_id", "password")
        for f in required:
            if not (attrs.get(f) or "").strip():
                raise serializers.ValidationError({f: "This field is required."})

        return attrs

    def create(self, validated_data):
        password = validated_data.pop("password")
        user = User(**validated_data)
        user.set_password(password)
        user.save()

        # default role (base user / citizen)
        citizen_role, _ = Role.objects.get_or_create(
            name="Base user", defaults={"description": "Default role for newly registered users (Base user)"}
        )
        UserRole.objects.get_or_create(user=user, role=citizen_role)

        return user

class LoginSerializer(serializers.Serializer):
    identifier = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        identifier = (attrs["identifier"] or "").strip()
        password = attrs["password"]

        user = User.objects.filter(
            Q(username__iexact=identifier)
            | Q(email__iexact=identifier)
            | Q(phone__iexact=identifier)
            | Q(national_id__iexact=identifier)
        ).first()

        if not user or not user.check_password(password):
            raise AuthenticationFailed("Invalid credentials.")

        refresh = RefreshToken.for_user(user)

        return {
            "access": str(refresh.access_token),
            "refresh": str(refresh),
            "user": UserPublicWithRolesSerializer(user).data,
        }
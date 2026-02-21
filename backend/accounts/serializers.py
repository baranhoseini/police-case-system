from django.contrib.auth import get_user_model
from django.db.models import Q
from rest_framework import serializers
from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.tokens import RefreshToken

from django.contrib.auth import get_user_model
from rest_framework import serializers
from rbac.models import Role, UserRole


User = get_user_model()



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
            name="Citizen", defaults={"description": "Default role for newly registered users"}
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
            "user": UserPublicSerializer(user).data,
        }
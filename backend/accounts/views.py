from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from drf_spectacular.utils import extend_schema, OpenApiResponse

from .serializers import RegisterSerializer, LoginSerializer, UserPublicSerializer


class RegisterView(APIView):
    @extend_schema(
        tags=["Auth"],
        request=RegisterSerializer,
        responses={201: UserPublicSerializer},
    )
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response(UserPublicSerializer(user).data, status=status.HTTP_201_CREATED)


class LoginView(APIView):
    @extend_schema(
        tags=["Auth"],
        request=LoginSerializer,
        responses={200: OpenApiResponse(description="JWT tokens + user info")},
    )
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.validated_data, status=status.HTTP_200_OK)


class MeView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=["Auth"],
        responses={200: UserPublicSerializer},
    )
    def get(self, request):
        return Response(UserPublicSerializer(request.user).data, status=status.HTTP_200_OK)

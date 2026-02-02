from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

class RegisterView(APIView):
    def post(self, request):
        return Response({"detail": "TODO: register"}, status=status.HTTP_501_NOT_IMPLEMENTED)

class LoginView(APIView):
    def post(self, request):
        return Response({"detail": "TODO: login"}, status=status.HTTP_501_NOT_IMPLEMENTED)

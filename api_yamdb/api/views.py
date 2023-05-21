from rest_framework import viewsets, permissions, generics
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.response import Response

from .serializers import TitleSerializer, SingUpSerializer, GetTokenSerializer
from reviews.models import Title, User


class TitleViewSet(viewsets.ModelViewSet):
    queryset = Title.objects.all()
    serializer_class = TitleSerializer
    permission_classes = []


class GetTokenView(TokenObtainPairView):
    """Получение токена"""
    permission_classes = [permissions.AllowAny]
    serializer_class = GetTokenSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        token = {
            'token': serializer.validated_data,
        }
        return Response(token)


class RegisterUserView(generics.CreateAPIView):
    """Регистрация пользователя"""
    queryset = User.objects.all()
    permission_classes = [permissions.AllowAny]
    serializer_class = SingUpSerializer

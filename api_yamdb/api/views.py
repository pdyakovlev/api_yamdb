from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics, permissions, status, viewsets
from rest_framework.serializers import ValidationError
from rest_framework.decorators import action
from rest_framework.filters import SearchFilter
from rest_framework.mixins import (CreateModelMixin, DestroyModelMixin,
                                   ListModelMixin)
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken

from django.core.mail import send_mail
from django.db import IntegrityError
from django.shortcuts import get_object_or_404
from django.contrib.auth.tokens import default_token_generator

from reviews.models import Category, Comment, Genre, Review, Title, User

from . import serializers
from .filters import TitleFilter
from .permissions import (AdminModeratorAuthorPermissions, AdminOnly,
                          IsAdminUserOrReadOnly)


class UserViewSet(viewsets.ModelViewSet):
    """Класс отвечающий за отображение пользователей."""

    queryset = User.objects.all()
    permission_classes = (permissions.IsAuthenticated, AdminOnly,)
    filter_backends = (SearchFilter,)
    search_fields = ['username', ]
    lookup_field = 'username'
    serializer_class = serializers.UserSerializer
    http_method_names = ["get", "post", "patch", "delete", "head", "options"]

    # ↓функция для обращения пользователя к данным собственного аккаунта↓

    @action(detail=False, permission_classes=[permissions.IsAuthenticated, ],
            methods=['get', 'patch'],
            serializer_class=serializers.UserSelfPatchSerializer)
    def me(self, request):
        user = self.request.user
        if request.method == 'GET':
            serializer = self.get_serializer(user)
            return Response(serializer.data, status=status.HTTP_200_OK)
        serializer = self.get_serializer(user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)


class TitleViewSet(viewsets.ModelViewSet):
    """Класс отвечающий за отображение произведений."""
    queryset = Title.objects.all()
    permission_classes = (IsAdminUserOrReadOnly,)
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ('name', 'year', 'genre', 'category',)
    filterset_class = TitleFilter

    def get_serializer_class(self):
        # Выбираем сериализатор в зависимости от запроса
        # Это нужно для записи полей genre и category по slug
        if self.action in ('list', 'retrieve'):
            return serializers.TitleSerializer
        return serializers.TitleWriteSerializer


class ReviewViewSet(viewsets.ModelViewSet):
    """Класс отвечающий за отображение отзывов."""
    serializer_class = serializers.ReviewSerializer
    permission_classes = [AdminModeratorAuthorPermissions]

    def get_title(self):
        return get_object_or_404(Title, pk=self.kwargs.get('title_id'))

    def get_queryset(self):
        return self.get_title().reviews.all()

    def perform_create(self, serializer):
        serializer.save(author=self.request.user, title=self.get_title())


class GenreViewsSet(CreateModelMixin, ListModelMixin,
                    DestroyModelMixin, viewsets.GenericViewSet):
    """Класс отвечающий за отображение списка жанров."""
    queryset = Genre.objects.all()
    serializer_class = serializers.GenreSerializer
    permission_classes = (IsAdminUserOrReadOnly,)
    filter_backends = (SearchFilter,)
    search_fields = ('name',)
    lookup_field = 'slug'


class BaseCategoryView(generics.GenericAPIView):
    """
    Базовое представление для категорий.
    """
    queryset = Category.objects.all()
    serializer_class = serializers.CategorySerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [SearchFilter]
    search_fields = ['name']


class CategoryListCreateView(BaseCategoryView, generics.ListCreateAPIView):
    """
    Представление для получения списка категорий и создания новых категории.
    """
    permission_classes = [IsAdminUserOrReadOnly]


class CategoryDestroyView(BaseCategoryView, generics.DestroyAPIView):
    """Представление для удаления категории по её slug."""
    permission_classes = [AdminOnly]
    lookup_field = 'slug'


class GetTokenView(TokenObtainPairView):
    """Получение токена"""
    permission_classes = [permissions.AllowAny]
    serializer_class = serializers.GetTokenSerializer

    def post(self, request, *args, **kwargs):
        try:
            user_name = request.POST.get('username')
            confirmation_code = request.POST.get('confirmation_code')
            if user_name == "" or user_name is None:
                return Response("username is required",
                                status=status.HTTP_400_BAD_REQUEST)
            user = User.objects.filter(username=user_name).first()
            if user is None:
                return Response(status=status.HTTP_404_NOT_FOUND)
            if not default_token_generator.check_token(user,
                                                       confirmation_code):
                raise ValidationError('Неверный код подтверждения.')
            refresh = RefreshToken.for_user(user)
            token = {
                'token': str(refresh.access_token)
            }
            return Response(token)
        except (IntegrityError):
            return Response(status=status.HTTP_400_BAD_REQUEST)


class RegisterUserView(generics.CreateAPIView):
    """Регистрация пользователя"""
    queryset = User.objects.all()
    permission_classes = [permissions.AllowAny]
    serializer_class = serializers.SignUpSerializer

    def post(self, request):
        try:
            user_name = request.POST.get('username')
            user = User.objects.filter(username=user_name).first()
            e_mail = request.POST.get('email')
            if user is not None and user.email is not None:
                resp = "Вы уже зарегестрированы."
                if user.email != e_mail:
                    resp = "Вы зарегестрированы с другим адресом эл. почты."
                    return Response(resp,
                                    status=status.HTTP_400_BAD_REQUEST)
                return Response(resp,
                                status=status.HTTP_200_OK)
            serializer = self.get_serializer(data=request.data)
            if serializer.is_valid():
                if serializer.validated_data["username"] == "me":
                    return Response(serializer.data,
                                    status=status.HTTP_400_BAD_REQUEST)
                user = serializer.save()
                # Генерируем код подтверждения
                confirmation_code = default_token_generator.make_token(user)
                user.confirmation_code = confirmation_code
                # Отправляем письмо
                send_mail(
                    subject='Код подтверждения',
                    message=f'Ваш код подтверждения: {confirmation_code}',
                    from_email='api_yamdb@example.com',  # Адрес отправителя
                    recipient_list=[user.email],  # Адрес получателя
                    fail_silently=False,  # Не сообщать об ошибках
                )
                user.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            else:
                return Response(serializer.errors,
                                status=status.HTTP_400_BAD_REQUEST)
        except (IntegrityError):
            error = "Электронная почта не соответствует имени пользователя."
            return Response(error,
                            status=status.HTTP_400_BAD_REQUEST)


class CommentViewSet(viewsets.ModelViewSet):
    """Отображение комментариев."""
    serializer_class = serializers.CommentSerializer
    permission_classes = (AdminModeratorAuthorPermissions,)

    def get_queryset(self):
        comments = Comment.objects.filter(
            review_id=self.kwargs.get('review_id'))
        return comments

    def perform_create(self, serializer):
        review = get_object_or_404(
            Review,
            id=self.kwargs.get('review_id')
        )
        return serializer.save(author=self.request.user, review=review)

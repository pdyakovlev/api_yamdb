from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics, permissions, status, viewsets
from rest_framework.serializers import ValidationError
from rest_framework.decorators import action
from rest_framework.filters import SearchFilter
from rest_framework import mixins
from rest_framework import views
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import AccessToken

from django.core.mail import send_mail
from django.db import IntegrityError
from django.shortcuts import get_object_or_404
from django.contrib.auth.tokens import default_token_generator

from reviews.models import Category, Comment, Genre, Review, Title, User

from . import serializers
from .filters import TitleFilter
from .permissions import (AdminModeratorAuthorPermissions, AdminOnly,
                          IsAdminUserOrReadOnly)
from api_yamdb import settings


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


class CategoryGenreListCreateDestroyViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    """
    Базовое представление для категорий и жанров.
    """
    lookup_field = 'slug'
    permission_classes = [IsAdminUserOrReadOnly]
    filter_backends = (SearchFilter,)
    search_fields = ('name',)


class CategoryViewSet(CategoryGenreListCreateDestroyViewSet):
    """Представление для категорий"""
    queryset = Category.objects.all()
    serializer_class = serializers.CategorySerializer


class GenreViewSet(CategoryGenreListCreateDestroyViewSet):
    """Представление для жанров"""
    queryset = Genre.objects.all()
    serializer_class = serializers.GenreSerializer


class GetTokenView(views.APIView):
    """Получение токена"""
    permission_classes = [permissions.AllowAny]
    serializer_class = serializers.GetTokenSerializer

    def post(self, request, *args, **kwargs):
        try:
            serializer = serializers.GetTokenSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            user = get_object_or_404(
                User,
                username=serializer.validated_data['username'],)

            if not default_token_generator.check_token(
                    user, serializer.validated_data['confirmation_code']):
                raise ValidationError('Неверный код подтверждения.')

            token = AccessToken().for_user(user)
            return Response({'token': str(token)})
        except (IntegrityError):
            return Response(status=status.HTTP_400_BAD_REQUEST)


class RegisterUserView(generics.CreateAPIView):
    """Регистрация пользователя"""
    queryset = User.objects.all()
    permission_classes = [permissions.AllowAny]
    serializer_class = serializers.SignUpSerializer

    def create(self, request, *args, **kwargs):
        user_name = request.POST.get('username')
        user = User.objects.filter(username=user_name).first()
        e_mail = request.POST.get('email')
        if user is not None and user.email is not None:
            if user.email != e_mail:
                resp = "Вы зарегестрированы с другим адресом эл. почты."
                return Response(resp,
                                status=status.HTTP_400_BAD_REQUEST)
            resp = "Вы уже зарегестрированы"
            return Response(resp,
                            status=status.HTTP_200_OK)
        # Тесты валятся на повторный запрос от существующего пользователя с
        # возвратом кода 200 и на создание админом с возвратом кода 200
        # если не проверять до serializer.is_valid,
        # после serializer.is_valid код в таком случае всегда 400
        serializer = serializers.SignUpSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            user, _ = User.objects.get_or_create(**serializer.validated_data)

        except IntegrityError:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        confirmation_code = default_token_generator.make_token(user)
        email_data = {
            'subject': 'Добро пожаловать на наш сайт!',
            'message': f'Ваш код подтверждения: {confirmation_code}',
            'from_email': settings.TOKEN_EMAIL,
            'recipient_list': [user.email], }

        send_mail(**email_data)
        return Response({'email': user.email, 'username': user.username})


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

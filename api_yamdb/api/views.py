from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.response import Response
from rest_framework import viewsets, generics, permissions
from rest_framework.filters import SearchFilter

from reviews.models import Title, Category, User, Genre, Review, Comment
from . import serializers
from django_filters.rest_framework import DjangoFilterBackend
from .permissions import (
    IsAdminUserOrReadOnly, AdminModeratorAuthorPermissions, AdminOnly
)
from .filters import TitleFilter
from django.shortcuts import get_object_or_404


class UserViewSet(viewsets.ModelViewSet):
    """Класс отвечающий за отображение пользователей."""
    queryset = User.objects.all()
    serializer_class = serializers.UserSerializer
    permission_classes = (permissions.IsAuthenticated, AdminOnly,)
    filter_backends = (SearchFilter,)
    search_fields = ('username',)


class TitleViewSet(viewsets.ModelViewSet):
    """
    Получить список всех объектов.
        Права доступа: Доступно без токена.
    Добавить новое произведение.
        Права доступа: Администратор.
        Нельзя добавлять произведения, которые еще не вышли
        (год выпуска не может быть больше текущего).
        При добавлении нового произведения
        требуется указать уже существующие категорию и жанр.
    Информация о произведении
        Права доступа: **Доступно без токена**
    Обновить информацию о произведении
        Права доступа: **Администратор**
    Удалить произведение.
        Права доступа: **Администратор**.
    """
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
    """
    Получить список всех отзывов.
        Права доступа: **Доступно без токена**.
    Добавить новый отзыв. Пользователь может оставить
    только один отзыв на произведение.
        Права доступа: **Аутентифицированные пользователи.**
    Получить отзыв по id для указанного произведения.
        Права доступа: **Доступно без токена.**
    Частично обновить отзыв по id.
        Права доступа: **Автор отзыва, модератор или администратор.**
    Удалить отзыв по id
        Права доступа: **Автор отзыва, модератор или администратор.**
    """
    serializer_class = serializers.ReviewSerializer
    permission_classes = [AdminModeratorAuthorPermissions]

    def get_queryset(self):
        """Получаем все отзывы к произведению."""
        title = get_object_or_404(Title, id=self.kwargs['title_id'])
        return title.reviews.all()
    serializer_class = serializers.ReviewSerializer


class GenreViewsSet(viewsets.ModelViewSet):
    """Получение списка жанров."""
    queryset = Genre.objects.all()
    serializer_class = serializers.GenreSerializer
    permission_classes = (IsAdminUserOrReadOnly,)
    filter_backends = (SearchFilter,)
    search_fields = ('name',)


class CategoryListCreateView(
    generics.ListCreateAPIView,
    generics.CreateAPIView,
):
    """
    Представление для получения списка категорий и создания новых категории.
    """
    queryset = Category.objects.all()
    serializer_class = serializers.CategorySerializer
    permission_classes = (IsAdminUserOrReadOnly,)
    # позже добавлю свой prtmission
    # permission_classes = [permissions.AllowAny]


class CategoryDestroyView(generics.DestroyAPIView):
    """Представление для удаления категории по её slug."""
    queryset = Category.objects.all()
    serializer_class = serializers.CategorySerializer
    permission_classes = (AdminOnly,)
    # указываем поле slug, которое будет использоваться для идентификации
    # категории при удалении
    lookup_field = 'slug'

    # Только администратор может добавлять и удалять категории
    # permission_classes = [permissions.IsAdminUser]
    # добавлю после подключения токенов


class GetTokenView(TokenObtainPairView):
    """Получение токена"""
    permission_classes = [permissions.AllowAny]
    serializer_class = serializers.GetTokenSerializer

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
    serializer_class = serializers.SingUpSerializer


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

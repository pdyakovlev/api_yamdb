from rest_framework import viewsets, generics
from rest_framework.filters import SearchFilter
from rest_framework.filters import SearchFilter
from reviews.models import Title, Category, User, Genre
from .serializers import (TitleSerializer, TitleWriteSerializer,
                          CategorySerializer, CommentSerializer,
                          UserSerializer, ReviewSerializer, ReviewSerializer,
                          GenreSerializer)
from django_filters.rest_framework import DjangoFilterBackend
from .filters import TitleFilter
from .permissions import AdminModeratorAuthorPermissions
from django.shortcuts import get_object_or_404
from reviews.models import Review


class UserViewSet(viewsets.ModelViewSet):
    """Класс отвечающий за отображение пользователей."""
    queryset = User.objects.all()
    serializer_class = UserSerializer
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
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ('name', 'year', 'genre', 'category',)
    filterset_class = TitleFilter

    def get_serializer_class(self):
        # Выбираем сериализатор в зависимости от запроса
        # Это нужно для записи полей genre и category по slug
        if self.action in ('list', 'retrieve'):
            return TitleSerializer
        return TitleWriteSerializer


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
    serializer_class = ReviewSerializer
    permission_classes = (AdminModeratorAuthorPermissions)

    def get_queryset(self):
        """Получаем все отзывы к произведению."""
        title = get_object_or_404(Title, id=self.kwargs['title_id'])
        return title.reviews.all()
    serializer_class = ReviewSerializer


class GenreViewsSet(viewsets.ModelViewSet):
    """Получение списка жанров."""
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    filter_backends = (SearchFilter,)
    search_fields = ('name',)

    def perform_create(self, serializer):
        title = get_object_or_404(
            Title,
            id=self.kwargs.get('title_id')
        )
        serializer.save(author=self.request.user, title=title)

    def perform_create(self, serializer):
        title = get_object_or_404(
            Title,
            id=self.kwargs.get('title_id')
        )
        serializer.save(author=self.request.user, title=title)


class CategoryListCreateView(
    generics.ListCreateAPIView,
    generics.CreateAPIView,
):
    """
    Представление для получения списка категорий и создания новых категории.
    """
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    # позже добавлю свой prtmission
    # permission_classes = [permissions.AllowAny]


class CategoryDestroyView(generics.DestroyAPIView):
    """Представление для удаления категории по её slug."""
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    # указываем поле slug, которое будет использоваться для идентификации
    # категории при удалении
    lookup_field = 'slug'

    # Только администратор может добавлять и удалять категории
    # permission_classes = [permissions.IsAdminUser]
    # добавлю после подключения токенов


class CommentViewSet(viewsets.ModelViewSet):
    """Отображение комментариев."""
    serializer_class = CommentSerializer
    permission_classes = (AdminModeratorAuthorPermissions,)

    def get_queryset(self):
        review = get_object_or_404(
            Review,
            id=self.kwargs.get('review_id')
        )
        return review.comments.all()

    def perform_create(self, serializer):
        review = get_object_or_404(
            Review,
            id=self.kwargs.get('review_id')
        )
        return serializer.save(author=self.request.user, review=review)

from rest_framework import viewsets
from reviews.models import Title
from .serializers import TitleSerializer, TitleWriteSerializer
from django_filters.rest_framework import DjangoFilterBackend
from .filters import TitleFilter
from django.shortcuts import get_object_or_404


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
    def get_queryset(self):
        """Получаем все отзывы к произведению."""
        title = get_object_or_404(Title, id=self.kwargs['title_id'])
        return title.reviews.all()

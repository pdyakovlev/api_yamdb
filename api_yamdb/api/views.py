from rest_framework import viewsets
from reviews.models import Title
from .serializers import TitleSerializer, TitleWriteSerializer
from django_filters.rest_framework import DjangoFilterBackend
from .filters import TitleFilter
from rest_framework import permissions


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

    """
    queryset = Title.objects.all()
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ('name', 'year', 'genre', 'category',)
    filterset_class = TitleFilter
    permission_classes = []

    def get_serializer_class(self):
        if self.action in permissions.SAFE_METHODS:
            return TitleSerializer
        return TitleWriteSerializer

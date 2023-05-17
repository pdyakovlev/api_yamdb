from rest_framework import viewsets
from reviews.models import Title
from .serializers import TitleSerializer
from django_filters.rest_framework import DjangoFilterBackend
from .filters import TitleFilter


class TitleViewSet(viewsets.ModelViewSet):
    queryset = Title.objects.all()
    serializer_class = TitleSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ('name', 'year', 'genre', 'category',)
    filterset_class = TitleFilter
    permission_classes = []

from rest_framework_simplejwt.views import TokenObtainPairView
from django.db import IntegrityError
from rest_framework.response import Response
from rest_framework import viewsets, generics, permissions
from rest_framework.filters import SearchFilter
from rest_framework.mixins import (CreateModelMixin, DestroyModelMixin,
                                   ListModelMixin)
from rest_framework import status
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from django.core.mail import send_mail
from django.utils.crypto import get_random_string
from reviews.models import Title, Category, User, Genre, Review, Comment
from . import serializers
from .permissions import (
    IsAdminUserOrReadOnly, AdminModeratorAuthorPermissions, AdminOnly
)
from .filters import TitleFilter
from django.shortcuts import get_object_or_404
from django.core.mail import send_mail
from rest_framework.decorators import action


class UserViewSet(viewsets.ModelViewSet):
    """Класс отвечающий за отображение пользователей."""

    queryset = User.objects.all()
    permission_classes = (permissions.IsAuthenticated, AdminOnly,)
    filter_backends = (SearchFilter,)
    search_fields = ['username', ]
    lookup_field = 'username'
    serializer_class = serializers.UserSerializer
    http_method_names = ["get", "post", "patch", "delete", "head", "options"]

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


class GenreViewsSet(CreateModelMixin, ListModelMixin,
                    DestroyModelMixin, viewsets.GenericViewSet):
    """Получение списка жанров."""
    queryset = Genre.objects.all()
    serializer_class = serializers.GenreSerializer
    permission_classes = (IsAdminUserOrReadOnly,)
    filter_backends = (SearchFilter,)
    search_fields = ('name',)
    lookup_field = 'slug'


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
    filter_backends = (SearchFilter,)
    search_fields = ('name', )


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
        try:
            user_name = request.POST.get('username')
            if user_name == "" or user_name is None:
                return Response("username is required",
                                status=status.HTTP_400_BAD_REQUEST)
            user = User.objects.filter(username=user_name).first()
            if user is None:
                return Response(status=status.HTTP_404_NOT_FOUND)
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            token = {
                'token': serializer.validated_data,
            }
            return Response(token)
        except (IntegrityError):
            return Response(status=status.HTTP_400_BAD_REQUEST)


class RegisterUserView(generics.CreateAPIView):
    """Регистрация пользователя"""
    queryset = User.objects.all()
    permission_classes = [permissions.AllowAny]
    serializer_class = serializers.SingUpSerializer

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
                confirmation_code = get_random_string(length=6)
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

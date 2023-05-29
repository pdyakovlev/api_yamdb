import datetime as dt

from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from rest_framework_simplejwt.tokens import RefreshToken

from django.db.models import Avg
from django.shortcuts import get_object_or_404

from reviews.models import Category, Comment, Genre, Review, Title, User


class UserSerializer(serializers.ModelSerializer):
    """Сериализатор для модели пользователя."""

    email = serializers.EmailField(
        required=True, max_length=254,
        validators=[UniqueValidator(queryset=User.objects.all(),
                                    message='Адрес почты уже используется!')])

    username = serializers.RegexField(
        required=True, max_length=150, regex=r'^[\w.@+-]+$',
        validators=[UniqueValidator(queryset=User.objects.all(),
                                    message='Это имя пользователя занято!')])

    class Meta:
        model = User
        fields = (
            'username', 'email', 'first_name',
            'last_name', 'bio', 'role'
        )


class UserSelfPatchSerializer(UserSerializer):
    """Сериализатор для изменения пользователем своих данных."""
    role = serializers.CharField(read_only=True)


class NotAdminSerializer(serializers.ModelSerializer):
    """Сериализатор для модели пользователя без прав админа."""

    class Meta:
        model = User
        fields = (
            'username', 'email', 'first_name',
            'last_name', 'bio', 'role')
        read_only_fields = ('role',)


class SignUpSerializer(serializers.ModelSerializer):
    """Сериализатор регистрации пользователя."""

    username = serializers.RegexField(
        required=True, max_length=150, regex=r'^[\w.@+-]+$')

    class Meta:
        model = User
        fields = ('email', 'username')


class GetGenre(serializers.Field):
    """Получение данных о жанрах."""

    def to_representation(self, value):
        genre = []
        for val in value.all():
            genre.append({"name": val.name, "slug": val.slug})
        return genre


class GetCategory(serializers.Field):
    """Получение данных о категориях."""
    def to_representation(self, value):
        category = {"name": value.name, "slug": value.slug}
        return category


class GenreSerializer(serializers.ModelSerializer):
    """Сериализотор для модели Genre."""

    class Meta:
        model = Genre
        lookup_field = 'slug'
        fields = ('name', 'slug')


class CategorySerializer(serializers.ModelSerializer):
    """Сериализотор для модели Category."""
    class Meta:
        model = Category
        fields = ('name', 'slug')


class TitleSerializer(serializers.ModelSerializer):
    """Сериализотор для получения списка произведений."""
    genre = GetGenre()
    category = GetCategory()
    rating = serializers.SerializerMethodField()

    class Meta:
        model = Title
        fields = ('id', 'name', 'year', 'rating',
                  'description', 'genre', 'category')

    def get_rating(self, obj):
        raiting = Review.objects.filter(title_id=obj.id).aggregate(
            Avg('score')
        )['score__avg']
        if raiting is not None:
            return int(raiting)
        return raiting


class TitleWriteSerializer(serializers.ModelSerializer):
    """Сериализотор для записа/изменения данных о произведениях."""
    category = serializers.SlugRelatedField(
        queryset=Category.objects.all(),
        slug_field='slug',
    )

    genre = serializers.SlugRelatedField(
        queryset=Genre.objects.all(),
        slug_field='slug',
        many=True
    )

    class Meta:
        model = Title
        fields = ('id', 'name', 'year', 'genre', 'category', 'description')


class CommentSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Комментариев."""
    review = serializers.SlugRelatedField(
        slug_field='text',
        read_only=True
    )
    author = serializers.SlugRelatedField(
        slug_field='username',
        read_only=True
    )

    class Meta:
        model = Comment
        fields = ('id', 'author', 'review', 'text', 'pub_date')
        read_only_fields = ('pub_date',)

    def validate(self, data):
        """Добавляю дату"""
        data['pub_date'] = dt.datetime.now()
        return data


class ReviewSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Рейтингов."""
    title = serializers.SlugRelatedField(
        slug_field='name',
        read_only=True
    )
    author = serializers.SlugRelatedField(
        slug_field='username',
        read_only=True
    )

    def validate(self, data):
        """Проверка дубликатов оценки."""
        request = self.context['request']
        author = request.user
        title_id = self.context.get('view').kwargs.get('title_id')
        title = get_object_or_404(Title, pk=title_id)
        if (
            request.method == 'POST'
            and Review.objects.filter(title=title, author=author).exists()
        ):
            raise serializers.ValidationError(
                'Вы уже оставили отзыв этому произведению.'
            )
        data['title_id'] = title_id
        data['author'] = author
        data['pub_date'] = dt.datetime.now()
        return data

    class Meta:
        model = Review
        fields = ('id', 'author', 'title', 'text', 'score', 'pub_date')
        read_only_fields = ('pub_date',)


class GetTokenSerializer(serializers.Serializer):
    """Сериализатор для получения токена"""
    username = serializers.CharField()
    confirmation_code = serializers.CharField()

    def validate(self, attrs):
        user = User.objects.filter(username=attrs.get('username')).first()
        confirmation_code = attrs.get('confirmation_code')
        if user is not None:
            if confirmation_code != user.confirmation_code:
                raise serializers.ValidationError(
                    'The username and/or confirmation code is incorrect'
                )
        # создаем токены для пользователя
        refresh = RefreshToken.for_user(user)
        # возвращаем строковое представление токена доступа, вместо славаря
        return str(refresh.access_token)

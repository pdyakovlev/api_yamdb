from reviews.models import User
# ^Временно
from django.shortcuts import get_object_or_404
from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken
from reviews.models import Title, Genre, Category, Review, User
from rest_framework_simplejwt.tokens import RefreshToken
import datetime as dt


class GetGenre(serializers.Field):

    def to_representation(self, value):
        genre = []
        for val in value.all():
            genre.append({"name": val.name, "slug": val.slug})
        return genre


class GetCategory(serializers.Field):
    def to_representation(self, value):
        category = [{"name": value.name, "slug": value.slug}]
        return category


class TitleSerializer(serializers.ModelSerializer):

    genre = GetGenre()
    category = GetCategory()

    class Meta:
        model = Title
        fields = ('id', 'name', 'year', 'rating',
                  'description', 'genre', 'category')


class TitleWriteSerializer(serializers.ModelSerializer):

    category = serializers.SlugRelatedField(
        queryset=Category.objects.all(),
        slug_field='slug'
    )
    genre = serializers.SlugRelatedField(
        queryset=Genre.objects.all(),
        slug_field='slug',
        many=True
    )

    def validate_year(self, value):
        year = dt.date.today().year
        if value > year:
            raise serializers.ValidationError('Произведение ещё не вышло!')
        return value

    class Meta:
        model = Title
        fields = ('name', 'year', 'genre', 'category')
        


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['name', 'slug']


class ReviewSerializer(serializers.ModelSerializer):

    # serializers.SlugRelatedField ищет в связанной базе данных (user)
    # поле username и присваивает его.
    author = serializers.SlugRelatedField(
        read_only=True,
        slug_field='username',
    )

    class Meta:
        model = Review
        fields = ('id', 'text', 'author', 'score', 'pub_date')
        read_only_fields = ('title', 'pub_date', 'author')

    def validate(self, data):
        if self.context['request'].method == 'POST':
            user = User.objects.create_user(
                username='6TestUser',
                email='Test6@Test')
            author = user
            # ^ Временно
            # author = self.context['request'].user
            title_id = self.context['view'].kwargs['title_id']
            title = get_object_or_404(Title, id=title_id)
            if Review.objects.filter(title=title, author=author).exists():
                raise serializers.ValidationError(
                    'Вы уже оставляли отзыв к этому произведению')
            data['author'] = author
            data['pub_date'] = dt.datetime.now()
            data['title'] = title

        return data


class SingUpSerializer(serializers.ModelSerializer):
    """Сериализатор регистрации пользователя"""
    class Meta:
        model = User
        fields = ('email', 'username')


class GetTokenSerializer(serializers.Serializer):
    """Сериализатор для получения токена"""
    username = serializers.CharField()
    # confirmation_code = serializers.CharField()

    def validate(self, attrs):
        user = User.objects.filter(username=attrs.get('username')).first()
        # confirmation_code = attrs.get('confirmation_code')
        # if user is None or confirmation_code != user.confirmation_code:
        if user is None:
            raise serializers.ValidationError(
                'The username and/or confirmation code is incorrect'
            )
        # создаем токены для пользователя
        refresh = RefreshToken.for_user(user)
        # возвращаем строковое представление токена доступа, вместо славаря
        return str(refresh.access_token)


class SingUpSerializer(serializers.ModelSerializer):
    """Сериализатор регистрации пользователя"""
    class Meta:
        model = User
        fields = ('email', 'username')


class GetTokenSerializer(serializers.Serializer):
    """Сериализатор для получения токена"""
    username = serializers.CharField()
    # confirmation_code = serializers.CharField()

    def validate(self, attrs):
        user = User.objects.filter(username=attrs.get('username')).first()
        # confirmation_code = attrs.get('confirmation_code')
        # if user is None or confirmation_code != user.confirmation_code:
        if user is None:
            raise serializers.ValidationError(
                'The username and/or confirmation code is incorrect'
            )
        # создаем токены для пользователя
        refresh = RefreshToken.for_user(user)
        # возвращаем строковое представление токена доступа, вместо славаря
        return str(refresh.access_token)

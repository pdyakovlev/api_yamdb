from rest_framework import serializers
from reviews.models import Title, Genre, Category
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
        fields = ('name', 'year', 'genre', 'category')


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

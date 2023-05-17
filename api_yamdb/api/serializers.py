from rest_framework import serializers
from reviews.models import Title


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

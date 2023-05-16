from rest_framework import serializers
from reviews.models import Title


class TitleSerializer(serializers.ModelSerializer):
    name = serializers.CharField()
    # year = serializers.IntegerField()
    # genre = serializers.ManyRelatedField()
    # category = serializers.PrimaryKeyRelatedField()

    class Meta:
        model = Title
        fields = '__all__'

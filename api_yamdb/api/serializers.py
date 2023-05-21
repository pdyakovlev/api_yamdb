from rest_framework import serializers
from reviews.models import Title, User
from rest_framework_simplejwt.tokens import RefreshToken


class TitleSerializer(serializers.ModelSerializer):
    name = serializers.CharField()
    # year = serializers.IntegerField()
    # genre = serializers.ManyRelatedField()
    # category = serializers.PrimaryKeyRelatedField()

    class Meta:
        model = Title
        fields = '__all__'


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

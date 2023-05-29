from django.utils import timezone
from rest_framework.exceptions import ValidationError
import re


def year_validator(value):
    if value > timezone.localtime(timezone.now()).year:
        raise ValidationError('Год не должен быть больше текущего')


def validate_username(value):
    if value == 'me':
        raise ValidationError(
            ('Имя пользователя не может быть <me>.'),
            params={'value': value},
        )


def validate_username_bad_sign(value):
    if re.search(r'^[a-zA-Z][a-zA-Z0-9-_\.]{1,20}$', value) is None:
        raise ValidationError(
            (f'Не допустимые символы <{value}> в нике.'),
            params={'value': value},
        )

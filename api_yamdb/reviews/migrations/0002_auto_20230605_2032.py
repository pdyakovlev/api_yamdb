# Generated by Django 3.2 on 2023-06-05 15:32

import django.core.validators
from django.db import migrations, models
import reviews.validators


class Migration(migrations.Migration):

    dependencies = [
        ('reviews', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='title',
            name='rating',
        ),
        migrations.AlterField(
            model_name='comment',
            name='pub_date',
            field=models.DateTimeField(auto_now_add=True, db_index=True, verbose_name='Дата публикации'),
        ),
        migrations.AlterField(
            model_name='review',
            name='pub_date',
            field=models.DateTimeField(auto_now_add=True, db_index=True, verbose_name='Дата публикации'),
        ),
        migrations.AlterField(
            model_name='review',
            name='score',
            field=models.IntegerField(error_messages={'validators': 'Оценка от 1 до 10!'}, validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(10)], verbose_name='Рейтинг'),
        ),
        migrations.AlterField(
            model_name='title',
            name='year',
            field=models.PositiveSmallIntegerField(validators=[reviews.validators.year_validator], verbose_name='Год'),
        ),
        migrations.AlterField(
            model_name='user',
            name='email',
            field=models.EmailField(default='default@mail.ru', max_length=254, unique=True, verbose_name='Электронная почта'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='user',
            name='role',
            field=models.CharField(choices=[('user', 'пользователь'), ('moderator', 'модератор'), ('admin', 'администратор')], default='user', max_length=9, verbose_name='Права доступа'),
        ),
        migrations.AlterField(
            model_name='user',
            name='username',
            field=models.CharField(max_length=150, unique=True, validators=[reviews.validators.validate_username, reviews.validators.validate_username_bad_sign], verbose_name='Имя пользователя'),
        ),
        migrations.AddConstraint(
            model_name='review',
            constraint=models.UniqueConstraint(fields=('title', 'author'), name='unique review'),
        ),
    ]

from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """Класс описывающий создание пользователя."""
    ROLES = (("user", "User"),
             ("moderator", "Moderator"),
             ("admin", "Admin"))
    username = models.CharField(
        verbose_name='Имя пользователя',
        max_length=150,
        unique=True,
        blank=False,
        null=False
    )
    email = models.EmailField(
        verbose_name='Электронная почта',
        max_length=254,
        blank=False,
        unique=True
    )
    role = models.CharField(
        verbose_name='Права доступа',
        choices=ROLES,
        default="user",
        max_length=10
    )
    bio = models.TextField(
        verbose_name='Биография',
        null=True,
        blank=True
    )
    first_name = models.CharField(
        verbose_name='Имя',
        max_length=150,
        blank=True
    )
    last_name = models.CharField(
        verbose_name='Фамилия',
        max_length=150,
        blank=True
    )
    confirmation_code = models.CharField(
        verbose_name='код подтверждения',
        max_length=254,
        null=True,
        blank=False,
        default='XXXX'
    )

    @property
    def is_user(self):
        return self.role == 'user'

    @property
    def is_moderator(self):
        return self.role == 'moderator'

    @property
    def is_admin(self):
        return self.role == 'admin'

    class Meta:
        ordering = ('id',)
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return self.username


class Category(models.Model):
    """Класс описывающий категории."""
    name = models.CharField(verbose_name='Имя', max_length=256)
    slug = models.SlugField(verbose_name='Ссылка', max_length=50, unique=True)

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'

    def __str__(self):
        return self.name


class Genre(models.Model):
    """Класс описывающий жанры."""
    name = models.CharField(max_length=256)
    slug = models.SlugField(max_length=50, unique=True)

    class Meta:
        verbose_name = 'Жанр'
        verbose_name_plural = 'Жанры'

    def __str__(self):
        return self.name


class Title(models.Model):
    """
    Класс описывающий произведения.
    """
    name = models.CharField(verbose_name='Имя', max_length=256)
    year = models.PositiveSmallIntegerField(verbose_name='Год')
    genre = models.ManyToManyField(
        Genre,
        verbose_name='Жанр',
        related_name='titles',
        through='GenreTitle')
    category = models.ForeignKey(
        Category, verbose_name='Категория', on_delete=models.CASCADE
    )
    rating = models.IntegerField(
        verbose_name='Рейтинг', null=True, blank=True,
        default=None)
    description = models.CharField(
        verbose_name='Описание', max_length=256, default="Без описания"
    )

    class Meta:
        verbose_name = 'Произведение'
        verbose_name_plural = 'Произведения'

    def __str__(self):
        return self.name


class GenreTitle(models.Model):
    title = models.ForeignKey(Title, on_delete=models.CASCADE)
    genre = models.ForeignKey(Genre, on_delete=models.CASCADE)


class Review(models.Model):
    """Класс описывающий рейтинг."""
    author = models.ForeignKey(
        User, verbose_name='Автор', on_delete=models.CASCADE
    )
    title = models.ForeignKey(
        Title, verbose_name='Название', on_delete=models.CASCADE,
        related_name="reviews"
    )
    text = models.TextField('Текст')
    score = models.IntegerField('Рейтинг')
    pub_date = models.DateTimeField('Дата публикации')

    class Meta:
        verbose_name = 'Рейтинг'
        verbose_name_plural = 'Рейтинг'

    def __str__(self):
        return str(self.title)


class Comment(models.Model):
    """Класс описывающий комментарии."""
    author = models.ForeignKey(
        User, verbose_name='Автор', on_delete=models.CASCADE
    )
    review = models.ForeignKey(
        Review, verbose_name='Рейтинг', on_delete=models.CASCADE
    )
    text = models.TextField('Текст')
    pub_date = models.DateTimeField('Дата публикации')

    class Meta:
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'

    def __str__(self):
        return str(self.text)

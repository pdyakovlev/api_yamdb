from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    ROLES = (("user", "User"),
             ("moderator", "Moderator"),
             ("admin", "Admin"))
    email = models.EmailField(null=True, blank=False, unique=True)
    role = models.CharField(choices=ROLES, default="user", max_length=10)
    bio = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.username


class Category(models.Model):
    name = models.CharField(max_length=256)
    slug = models.SlugField(max_length=50, unique=True)

    def __str__(self):
        return self.name


class Genre(models.Model):
    name = models.CharField(max_length=256)
    slug = models.SlugField(max_length=50, unique=True)

    def __str__(self):
        return self.name


class Title(models.Model):
    name = models.CharField(max_length=256)
    year = models.PositiveSmallIntegerField()
    genre = models.ManyToManyField(
        Genre,
        related_name='titles',
        through='GenreTitle')
    category = models.ForeignKey(Category, on_delete=models.CASCADE)

    def __str__(self):
        return self.name


class GenreTitle(models.Model):
    genre = models.ForeignKey(Title, on_delete=models.CASCADE)
    title = models.ForeignKey(Genre, on_delete=models.CASCADE)


class Review(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.ForeignKey(Title, on_delete=models.CASCADE)
    text = models.TextField()
    score = models.IntegerField()
    pub_date = models.DateTimeField()

    def __str__(self):
        return str(self.title)


class Comment(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    review = models.ForeignKey(Review, on_delete=models.CASCADE)
    text = models.TextField()
    pub_date = models.DateTimeField()

    def __str__(self):
        return str(self.text)

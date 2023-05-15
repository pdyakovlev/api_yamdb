from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    ROLES = (("user", "User"),
             ("moderator", "Moderator"),
             ("admin", "Admin"))
    email = models.EmailField(blank=False, unique=True)
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
    description = models.CharField(max_length=250)
    genre = models.ManyToManyField()
    category = models.ForeignKey()

    def __str__(self):
        return self.name


class GenreTitle(models.Model):
    genre = models.ForeignKey()
    title = models.ForeignKey()


class Review(models.Model):
    author = models.ForeignKey()
    title = models.ForeignKey()
    text = models.TextField()
    score = models.IntegerField()
    pub_date = models.DateTimeField()

    def __str__(self):
        return str(self.title)


class Comment(models.Model):
    author = models.ForeignKey()
    review = models.ForeignKey()
    text = models.TextField()
    pub_date = models.DateTimeField()

    def __str__(self):
        return str(self.text)

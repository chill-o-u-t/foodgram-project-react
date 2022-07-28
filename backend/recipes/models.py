from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class Tag(models.Model):
    title = models.CharField(
        max_length=16
    )
    color = models.CharField(
        max_length=7
    )
    slug = models.SlugField(
        unique=True,
        max_length=16
    )


class Ingredients(models.Model):
    title = models.CharField(
        max_length=150
    )
    quantity = models.IntegerField()
    units = models.CharField(
        choices='',
        max_length=16
    )


class Recipe(models.Model):
    author = models.ForeignKey(
        User,
        verbose_name='Автор',
        on_delete=models.CASCADE
    )
    title = models.CharField(
        max_length=150,
    )
    image = models.ImageField(
        upload_to=''
    )
    description = models.TextField()
    ingredients = models.ManyToManyField(
        to=Ingredients
    )
    tags = models.ManyToManyField(
        to=Tag
    )
    cooking_time = models.IntegerField()

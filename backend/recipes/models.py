import re

from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models

from backend.recipes.utils import SYMBOLS_TAG, SYMBOLS_USERNAME


class UserValidateMixin:
    def validate_username(self, value):
        if not re.match(SYMBOLS_USERNAME, value):
            raise ValidationError(
                'Недопустимое имя пользователя!'
            )
        return value


class User(AbstractUser, UserValidateMixin):
    email = models.EmailField(
        max_length=254,
        unique=True,
        null=False,
        blank=False
    )
    username = models.CharField(
        max_length=150,
        unique=True,
        null=False
    )
    first_name = models.CharField(
        max_length=150
    )
    last_name = models.CharField(
        max_length=150
    )

    @property
    def is_admin(self):
        return self.is_staff


class TagValidateMixin:
    def validate_slug(self, value):
        if not re.match(SYMBOLS_TAG, value):
            raise ValidationError(
                'Недопустимые символы в slug'
            )
        return value

    def validate_color(self, value):
        pass


class Tag(models.Model, TagValidateMixin):
    name = models.CharField(
        max_length=200,
        null=False
    )
    color = models.CharField(
        max_length=7,
        null=True
    )
    slug = models.SlugField(
        unique=True,
        max_length=200,
        null=True,
    )


class Ingredients(models.Model):
    name = models.CharField(
        max_length=200,
        null=False
    )
    measurement_unit = models.CharField(
        choices='',
        max_length=200,
        null=False
    )


class Recipe(models.Model):
    author = models.ForeignKey(
        User,
        verbose_name='Автор',
        on_delete=models.CASCADE,
        related_name='recipes',
        null=False
    )
    name = models.CharField(
        max_length=200,
        null=False
    )
    image = models.ImageField(
        upload_to='',
        null=False
    )
    description = models.TextField()
    ingredients = models.ManyToManyField(
        Ingredients,
        related_name='recipes',
        verbose_name='Ингридиенты',
        null=False
    )
    tags = models.ManyToManyField(
        Tag,
        verbose_name='Тэг',
        related_name='recipes',
    )
    cooking_time = models.IntegerField(
        validators=MinValueValidator(1),
        null=False
    )


class Follow(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following'
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=('user', 'author'), name='follow_unique'),
            models.CheckConstraint(
                check=~models.Q(user=models.F('author')),
                name='users_cannot_follow_themselves'
            )
        ]
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'

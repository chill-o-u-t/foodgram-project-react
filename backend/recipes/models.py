from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator
from django.db import models
from django.db.models import PositiveSmallIntegerField

from recipes.validators import (
    TagValidateMixin,
    UserValidateMixin
)


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
    )
    first_name = models.CharField(
        max_length=150
    )
    last_name = models.CharField(
        max_length=150
    )
    password = models.CharField(
        max_length=200,
    )

    @property
    def is_admin(self):
        return self.is_staff


class Tag(models.Model, TagValidateMixin):
    name = models.CharField(
        max_length=200,
        null=False,
    )
    color = models.CharField(
        max_length=7,
        null=True
    )
    slug = models.SlugField(
        unique=True,
        max_length=200,
    )
    author = models.ForeignKey(
        User,
        related_name='tags',
        on_delete=models.CASCADE
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
    )
    name = models.CharField(
        max_length=200,
    )
    image = models.ImageField(
        upload_to='recipes/',
        null=False,
        blank=True
    )
    description = models.TextField()
    ingredients = models.ManyToManyField(
        Ingredients,
        related_name='recipes',
        verbose_name='Ингридиенты',
        through='RecipeIngredient'
    )
    tags = models.ManyToManyField(
        Tag,
        verbose_name='Тэг',
        related_name='recipes',
    )
    cooking_time = models.IntegerField(
        validators=[MinValueValidator(1)],
        default=0,
        null=False
    )
    pub_date = models.DateTimeField(
        auto_now_add=True,
        db_index=True
    )
    cart = models.ManyToManyField(
        User,
        verbose_name='Список покупок',
        related_name='carts',
    )

    class Meta:
        ordering = ('-pub_date',)

    def __str__(self):
        return self.name[:15]


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


class Favourite(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        related_name='favourites',
        on_delete=models.CASCADE
    )
    author = models.ForeignKey(
        User,
        related_name='favourites',
        on_delete=models.CASCADE
    )


class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        related_name='ingridient',
        on_delete=models.CASCADE
    )
    ingredients = models.ForeignKey(
        Ingredients,
        related_name='recipe',
        on_delete=models.CASCADE
    )
    amount = PositiveSmallIntegerField(
        default=0,
        validators=[MinValueValidator(1)]
    )

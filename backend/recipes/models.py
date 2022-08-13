from django.core.validators import MinValueValidator
from django.db import models
from django.db.models import PositiveSmallIntegerField

from recipes.validators import (
    TagValidateMixin,
    UserValidateMixin
)
from users.models import User


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


class Ingredient(models.Model):
    name = models.CharField(
        max_length=200,
        null=False
    )
    measurement_unit = models.CharField(
        max_length=200,
        null=False
    )

    def __str__(self):
        return self.name[:15]


class Recipe(models.Model):
    author = models.ForeignKey(
        User,
        verbose_name='Автор',
        on_delete=models.CASCADE,
        related_name='recipes',
    )
    name = models.CharField(
        max_length=200,
        verbose_name='Название рецепта',
    )
    image = models.ImageField(
        upload_to='recipes/',
        null=False,
        blank=True,
        verbose_name='Изображение',
    )
    text = models.TextField()
    ingredient = models.ManyToManyField(
        Ingredient,
        related_name='recipes',
        verbose_name='Ингридиенты',
        through='IngredientAmount'
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

    class Meta:
        ordering = ('-id',)

    def __str__(self):
        return self.name[:15]


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


class IngredientAmount(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='ingredients'
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        related_name='recipe'
    )
    amount = PositiveSmallIntegerField(
        default=0,
        validators=[MinValueValidator(1)]
    )

    def __str__(self):
        return "{}{}".format(self.recipe.__str__(), self.ingredient.__str__())


class Cart(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='carts',
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='carts',
    )

    class Meta:
        ordering = ['-id']
        constraints = [
            models.UniqueConstraint(fields=['user', 'recipe'],
                                    name='unique cart user')
        ]
        verbose_name = 'Продуктовая корзина'
        verbose_name_plural = 'Продуктовые корзины'

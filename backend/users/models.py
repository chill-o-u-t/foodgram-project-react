from django.contrib.auth.models import AbstractUser
from django.db import models

from recipes.validators import UserValidateMixin


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

from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator

from .models import Follow, User
from recipes.models import Recipe


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        fields = (
            'username',
            'email',
            'first_name',
            'last_name',
            'password',
            'id'
        )
        extra_kwargs = {'password': {'write_only': True}}
        model = User


class FollowSerializer(serializers.ModelSerializer):
    user = serializers.SlugRelatedField(
        read_only=True,
        slug_field='username',
        default=UserSerializer
    )
    author = serializers.SlugRelatedField(
        slug_field='username',
        required=True,
        queryset=User.objects.all()
    )
    is_subscribed = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        fields = ('user', 'author')
        model = Follow
        validators = [
            UniqueTogetherValidator(
                queryset=Follow.objects.all(),
                fields=('user', 'following')
            )
        ]

    @property
    def get_user(self):
        return self.context.get('request').user

    def get_is_subscribed(self, obj):
        if self.get_user.is_anonymous:
            return False
        return Follow.objects.filter(
            user=self.get_user,
            author=obj.author
        )

    @property
    def get_recipes_count(self):
        return Recipe.author.objects.all().count()

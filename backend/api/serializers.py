from rest_framework import serializers

from recipes.models import Tag, Ingredients, Recipe, User, Follow, Favourite
from rest_framework.validators import UniqueTogetherValidator

from recipes.validators import UserValidateMixin


class TagSerializer(serializers.ModelSerializer):
    slug = serializers.SlugRelatedField(
        slug_field='slug',
        many=True
    )

    class Meta:
        model = Tag
        fields = ('title', 'color', 'id')


class IngredientsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredients
        fields = ('__all__',)


class RecipeSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        read_only=True,
        slug_field='username'
    )
    ingredients = serializers.SlugRelatedField(
        read_only=True,
        slug_field='ingredients'
    )
    tags = serializers.SlugRelatedField(
        read_only=True,
        slug_field='tags'
    )

    class Meta:
        model = Recipe
        fields = ('__all__',)


class FollowSerializer(serializers.ModelSerializer):
    user = serializers.SlugRelatedField(
        read_only=True,
        slug_field='username',
        default=serializers.CurrentUserDefault()
    )
    author = serializers.SlugRelatedField(
        slug_field='username',
        required=True,
        queryset=User.objects.all()
    )

    class Meta:
        fields = ('user', 'author')
        model = Follow
        validators = [
            UniqueTogetherValidator(
                queryset=Follow.objects.all(),
                fields=('user', 'following')
            )
        ]


class FavouriteSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        slug_field='username',
        read_only=True
    )
    recipe = serializers.SlugRelatedField(
        slug_field='recipe',
        required=True
    )

    class Meta:
        fields = ('author', 'recipe')
        model = Favourite


class UserSerializer(serializers.ModelSerializer, UserValidateMixin):
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

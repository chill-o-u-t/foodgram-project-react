from rest_framework import serializers

from recipes.models import Tag, Ingredients, Recipe, User, Favourite

from recipes.validators import UserValidateMixin


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ('title', 'color', 'id')
        read_only_fields = '__all__',


class IngredientsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredients
        fields = ('__all__',)
        read_only_fields = '__all__',


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


class FavouriteSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        slug_field='username',
        read_only=True,
        default=serializers.CurrentUserDefault()
    )
    recipe = serializers.SlugRelatedField(
        slug_field='recipe',
        required=True,
        queryset=Recipe.objects.all()
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

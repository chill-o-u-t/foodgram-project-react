from rest_framework import serializers

from recipes.models import Tag, Ingredients, Recipe


class TagSerializer(serializers.Serializer):
    slug = serializers.SlugRelatedField(
        slug_field='slug',
        many=True
    )

    class Meta:
        model = Tag
        fields = ('title', 'color')


class IngredientsSerializer(serializers.Serializer):
    class Meta:
        model = Ingredients
        fields = '__all__'


class RecipeSerializer(serializers.Serializer):
    author = serializers.SlugRelatedField(
        read_only=True,
        slug_field='author'
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

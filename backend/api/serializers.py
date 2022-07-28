from rest_framework import serializers

from backend.recipes.models import Tag, Ingredients


class TagSerializer(serializers.Serializer):
    class Meta:
        model = Tag
        fields = ('title', 'color')


class IngredientsSerializer(serializers.Serializer):
    class Meta:
        model = Ingredients
        fields = '__all__'

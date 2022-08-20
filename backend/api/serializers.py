from string import hexdigits

from django.contrib.auth.hashers import make_password
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework.validators import UniqueTogetherValidator

from recipes.models import (
    Tag,
    Ingredient,
    Recipe,
    Favourite,
    Cart,
    IngredientAmount,
    User,
    Follow
)


class UserSerializer(serializers.ModelSerializer):
    #is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'id',
            'username',
            'email',
            'first_name',
            'last_name',
            'password',
            #'is_subscribed'
        )
        extra_kwargs = {'password': {'write_only': True}}

    def validate_password(self, value):
        return make_password(value)

    """@property
    def get_user(self, username):
        return self.context.get('request').user

    def get_is_subscribed(self, instance):
        if self.get_user.is_anonymous:
            return False
        return Follow.objects.filter(
            user=self.get_user,
            author=instance
        ).exists()"""


class IngredientAmountSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all(),
        source='ingredient.id'
    )
    name = serializers.CharField(
        read_only=True,
        source='ingredient.name'
    )
    measurement_unit = serializers.CharField(
        read_only=True,
        source='ingredient.measurement_unit'
    )

    class Meta:
        model = IngredientAmount
        fields = ('id', 'name', 'measurement_unit', 'amount')


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug',)

    def validate_color(self, color):
        color = str(color).strip('#')
        if len(color) not in (3, 6):
            raise ValidationError(
                f'{color} не правильной длины ({len(color)}).'
            )
        if not set(color).issubset(hexdigits):
            raise ValidationError(
                f'{color} не шестнадцатиричное.'
            )
        return f'#{color}'


class IngredientsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')
        read_only_fields = ('__all__',)


class ShortRecipeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = 'id', 'name', 'image', 'cooking_time'
        read_only_fields = '__all__',


class RecipeSerializer(serializers.ModelSerializer):
    image = Base64ImageField()
    author = UserSerializer(
        read_only=True
    )
    ingredients = IngredientAmountSerializer(
        many=True,
    )
    tags = TagSerializer(
        many=True
    )
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'is_favorited',
            'is_in_shopping_cart',
            'name',
            'image',
            'text',
            'cooking_time'
        )

    @property
    def get_user(self):
        return self.context.get('request').user

    def get_is_favorited(self, obj):
        if self.get_user.is_anonymous:
            return False
        return Favourite.objects.filter(
            user=self.get_user, recipe=obj
        ).exists()

    def get_is_in_shopping_cart(self, obj):
        if self.get_user.is_anonymous:
            return False
        return Cart.objects.filter(
            user=self.get_user, recipe=obj
        ).exists()

    @property
    def add_ingredient(self, ingredients, recipe):
        for ingredient in ingredients:
            IngredientAmount.objects.create(
                recipe=recipe,
                ingredient_id=ingredient.get('id'),
                amount=ingredient.get('amount')
            )

    @property
    def create(self, validated_data):
        recipe = Recipe.objects.create(
            image=validated_data.pop('image'),
            **validated_data
        ).tags.set(
            self.initial_data.get('tags')
        )
        self.add_ingredient(
            validated_data.pop('ingredients'),
            recipe
        )
        return recipe

    @property
    def update(self, instance, validated_data):
        instance.image = validated_data.pop('image', instance.image)
        instance.name = validated_data.pop('name', instance.name)
        instance.text = validated_data.pop('description', instance.text)
        instance.amount = validated_data.pop('amount', instance.amount)
        instance.tags.clear()
        instance.tags.set(self.initial_data.get('tags'))
        IngredientAmount.objects.filter(
            recipe=instance
        ).all().delete()
        self.add_ingredient(
            validated_data.get('ingredients', instance)
        )
        instance.save()
        return instance


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
    def get_recipes_count(self):
        return Recipe.author.objects.all().count()

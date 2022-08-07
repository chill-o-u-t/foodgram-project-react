from rest_framework import serializers
from drf_extra_fields.fields import Base64ImageField

from recipes.models import Tag, Ingredient, Recipe, User, Follow, Favourite, Cart, IngredientAmount
from rest_framework.validators import UniqueTogetherValidator

from recipes.validators import UserValidateMixin


class IngredientAmountSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    amount = serializers.ReadOnlyField(source='ingredient.amount')

    class Meta:
        model = IngredientAmount
        fields = ('id', 'name', 'measurement_unit', 'amount')
        validators = [
            UniqueTogetherValidator(
                queryset=IngredientAmount.objects.all(),
                fields=['ingredient', 'recipe']
            )
        ]


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


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ('author', 'name', 'slug', 'color',)


class IngredientsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')
        read_only_fields = '__all__'


class RecipeSerializer(serializers.ModelSerializer):
    image = Base64ImageField()
    author = UserSerializer(
        read_only=True
    )
    ingredients = IngredientAmountSerializer(
        read_only=True,
        many=True,
        source='recipeingredient_set'
    )
    tags = TagSerializer(
        read_only=True,
        many=True
    )
    #is_favorited = serializers.SerializerMethodField()
    #is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            #'is_favorited',
            #'is_in_shopping_cart',
            'name',
            'image',
            'text',
            'cooking_time'
        )

    @property
    def get_user(self):
        return self.context.get('request').user

    @property
    def get_is_favorited(self, obj):
        if self.get_user.is_anonymous:
            return False
        return Favourite.objects.filter(
            favourites__user=self.get_user, id=obj.id
        ).exists()

    @property
    def get_is_in_shopping_cart(self, obj):
        if self.get_user.is_anonymous:
            return False
        return Cart.objects.filter(
            carts__user=self.get_user, id=obj.id
        )

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

    @property
    def get_is_subscribed(self, obj):
        if self.get_user.is_anonymous:
            return False
        return Follow.objects.filter(
            user=self.get_user,
            author=obj.author
        )

    @property
    def get_recipes_count(self):
        return Recipe.author.all().count()


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


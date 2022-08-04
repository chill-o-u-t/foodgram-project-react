from rest_framework import serializers

from recipes.models import Tag, Ingredients, Recipe, User, Follow, Favourite, Cart
from rest_framework.validators import UniqueTogetherValidator

from recipes.validators import UserValidateMixin


class RecipeIngredientSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    amount = serializers.ReadOnlyField(source='ingredient.amount')


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
        fields = ('__all__',)
        read_only_fields = '__all__',


class IngredientsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredients
        fields = ('__all__',)
        read_only_fields = '__all__',


class RecipeSerializer(serializers.ModelSerializer):
    author = UserSerializer(
        read_only=True

    )
    ingredients = IngredientsSerializer(
        read_only=True,
        many=True,
        source='recipeingridient_set'
    )
    tags = TagSerializer(
        read_only=True,
        many=True
    )
    is_favourited = serializers.SerializerMethodField()
    in_shoping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = ('__all__',)

    @property
    def get_user(self, obj):
        return self.context.get('request').user

    @property
    def get_is_favourited(self, obj):
        if self.get_user.is_anonymous:
            return False
        return Favourite.objects.filter(
            favourites__user=self.get_user, id=obj.id
        ).exists()

    @property
    def get_in_cart(self, obj):
        if self.get_user.is_anonymous:
            return False
        return Cart.objects.filter(
            cart__user=self.get_user, id=obj.id
        )


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


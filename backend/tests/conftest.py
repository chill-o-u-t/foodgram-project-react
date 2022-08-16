import pytest

from recipes.models import Recipe, Tag, Ingredient, User, IngredientAmount


@pytest.fixture
def user_password() -> str:
    return 'test'


@pytest.fixture
def user(user_password) -> User:
    email = 'test@terst.test'
    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        user = User.objects.create_user(
            username='TestUser',
            email=email,
            password=user_password,
        )
    return user


@pytest.fixture
def tag(user) -> Tag:
    tag, _ = Tag.objects.get_or_create(
        name='Test Tag #1',
        color='ffffff',
        slug='test',
        author=user,
    )
    return tag


@pytest.fixture
def ingredient() -> Ingredient:
    ingredient, _ = Ingredient.objects.get_or_create(
        name='test',
        measurement_unit='test',
    )
    return ingredient


@pytest.fixture
def recipe(user, tag) -> Recipe:
    recipe, _ = Recipe.objects.get_or_create(
        author=user,
        name='Recipe #1',
        text='Test recipe',
        cooking_time=1,
    )
    recipe.tags.add(tag)
    return recipe


@pytest.fixture
def recipe_ingredient(recipe, ingredient) -> IngredientAmount:
    ia, _ = IngredientAmount.objects.get_or_create(
        recipe=recipe,
        ingredient=ingredient,
        amount=1,
    )
    return ia

from django.db.models import F, Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from djoser.serializers import SetPasswordSerializer
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .filters import RecipeFilter
from .pagination import PagePagination
from .permissions import IsAdminOrAuthorOrReadOnly, AdminOrReadOnly
from recipes.models import (
    Tag,
    Ingredient,
    Recipe,
    Cart,
    Favourite,
    IngredientAmount,
    Follow,
    User
)
from .serializers import (
    UserSerializer,
    TagSerializer,
    IngredientsSerializer,
    RecipeSerializer,
    FollowSerializer,
    ShortRecipeSerializer
)


class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    permission_classes = (AdminOrReadOnly,)
    serializer_class = TagSerializer


class IngredientsViewSet(viewsets.ModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientsSerializer
    permission_classes = (AdminOrReadOnly,)


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter
    permission_classes = (IsAdminOrAuthorOrReadOnly,)
    pagination_class = PagePagination

    def get_queryset(self):
        is_f = self.request.query_params.get('is_favorited')
        if is_f is not None and int(is_f) == 1:
            return Recipe.objects.filter(favourites__user=self.request.user)
        is_c = self.request.query_params.get('is_in_shopping_cart')
        if is_c is not None and int(is_c) == 1:
            return Recipe.objects.filter(carts__user=self.request.user)
        return Recipe.objects.all()

    @property
    def get_user(self):
        return self.request.user

    def perform_create(self, serializer):
        serializer.save(
            author=self.get_user,
        )

    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=(IsAuthenticated,)
    )
    def shopping_cart(self, request, pk=None):
        if request.method == 'POST':
            return self.add_obj(Cart, pk)
        elif request.method == 'DELETE':
            return self.del_obj(Cart, pk)
        return None

    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=(IsAuthenticated,)
    )
    def favorite(self, request, pk=None):
        if request.method == 'POST':
            return self.add_obj(Favourite, pk)
        elif request.method == 'DELETE':
            return self.del_obj(Favourite, pk)
        return None

    def add_obj(self, model, pk):
        if model.objects.filter(
                user=self.get_user,
                id=pk
        ).exists():
            return Response('Уже существует', status=status.HTTP_400_BAD_REQUEST)
        recipe = get_object_or_404(Recipe, id=pk)
        model.objects.create(
            user=self.get_user,
            recipe=recipe
        )
        serializer = ShortRecipeSerializer(recipe)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def del_obj(self, model, pk):
        obj = model.objects.filter(
            user=self.get_user,
            recipe__id=pk
        )
        if not obj.exists():
            return Response(
                'Не существует', status=status.HTTP_400_BAD_REQUEST
            )
        obj.delete()
        return Response('', status=status.HTTP_204_NO_CONTENT)

    @action(
        methods=('get',),
        detail=False,
        permission_classes=(IsAuthenticated,)
    )
    def download_shopping_cart(self, request):
        if not self.get_user.carts.exists():
            return Response('Корзина пуста', status=status.HTTP_400_BAD_REQUEST)
        name = f'{self.get_user}_shopping_list'
        ingredients = IngredientAmount.objects.filter(
            recipe__carts__user=self.get_user
        ).values(
            ingredient_in=F('ingredient__name'),
            measure=F('ingredient__measurement_unit')
        ).annotate(amount=Sum('amount'))
        shopping_list = (f'Список покупок:{self.get_user}`a\n',)
        for ing in ingredients:
            shopping_list += (
                f'{ing["ingredient_in"]}: {ing["amount"]} {ing["measure"]}\n',
            )
        response = HttpResponse(
            shopping_list,
            content_type='text.txt; charset=utf-8'
        )
        response['Content-Disposition'] = f'attachment; filename={name}'
        return response


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    pagination_class = PagePagination
    lookup_field = 'id'

    def get_queryset(self):
        is_s = self.request.query_params.get('is_subscribed')
        if is_s is not None and int(is_s) == 1:
            return User.objects.filter(
                follower__user=self.request.user
            )
        return User.objects.all()

    @property
    def get_user(self):
        return self.request.user

    @action(
        methods=['get', 'patch'],
        detail=False,
        url_path='me',
        url_name='me'
    )
    def me(self, request):
        if self.request.method == 'PATCH':
            serializer = UserSerializer(
                request.user,
                data=request.data,
                partial=True,
                context={'request': request}
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)
        serializer = UserSerializer(request.user, partial=True, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(
        methods=('get',),
        detail=False,
        permission_classes=(IsAuthenticated,),
    )
    def subscriptions(self, request):
        pages = self.paginate_queryset(
            Follow.objects.filter(user=self.get_user)
        )
        serializer = FollowSerializer(
            pages,
            many=True,
            context={'request': request}
        )
        return self.get_paginated_response(serializer.data)

    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=(IsAuthenticated,),
    )
    def subscribe(self, request, id=None):
        author = get_object_or_404(User, id=id)
        if self.get_user == author:
            return Response(
                'Нельзя подписаться или отписаться от самого себя'
            )
        if request.method == 'DELETE':
            if not Follow.objects.filter(
                    user=self.get_user,
                    author=author
            ).exists():
                return Response(
                    'подписки не существует',
                    status=status.HTTP_400_BAD_REQUEST
                    )
            Follow.objects.filter(
                user=self.get_user,
                author=author
            ).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        if Follow.objects.filter(
                user=self.get_user,
                author=author
        ).exists():
            return Response(
                'подписка уже существует',
                status=status.HTTP_400_BAD_REQUEST
            )
        serializer = FollowSerializer(
            Follow.objects.create(
                user=self.get_user,
                author=author
            ),
            context={'request': request}
        )
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(
        methods=('post',),
        detail=False,
        permission_classes=(IsAuthenticated,),
        url_path='set_password',
        url_name='set_password'
    )
    def set_password(self, request):
        serializer = SetPasswordSerializer(
            data=request.data,
            context={'request': request}
        )
        serializer.is_valid()
        if not request.user.check_password(
            serializer.validated_data.get('current_password')
        ):
            return Response(
                {'current_password': 'incorrect'},
                status=status.HTTP_400_BAD_REQUEST
            )
        request.user.set_password(serializer.validated_data)
        request.user.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

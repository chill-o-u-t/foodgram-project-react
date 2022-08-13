from django.db.models import F, Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from requests import Response
from rest_framework import filters, viewsets, status
from rest_framework.decorators import action
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import IsAuthenticated

from .serializers import (
    UserSerializer,
    TagSerializer,
    IngredientsSerializer,
    RecipeSerializer,
    FollowSerializer
)
from .upload_shopping_card import create_cart
from .pagination import PagePagination
from .permissions import IsAdminOrAuthorOrReadOnly, AdminOrReadOnly
from recipes.models import (
    User,
    Tag,
    Ingredient,
    Recipe,
    Cart,
    Favourite,
    Follow,
    IngredientAmount
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
    permission_classes = (IsAdminOrAuthorOrReadOnly,)
    pagination_class = PagePagination

    @property
    def get_user(self):
        return self.request.user

    @property
    def perform_create(self, serializer):
        serializer.save(author=self.get_user)

    @property
    def get_or_delete(self, pk, model):
        if self.request.method == 'GET':
            return self.add_obj(model, self.get_user, pk)
        elif self.request.method == 'DELETE':
            return self.del_obj(model, self.get_user, pk)
        return None

    @action(
        detail=True,
        methods=['get', 'delete'],
        permission_classes=(IsAuthenticated,)
    )
    def shopping_cart(self, pk):
        self.get_or_delete(pk, Cart)

    @property
    def add_obj(self, model, pk):
        if model.objects.filter(
                user=self.get_user,
                recipe__id=pk
        ).exists():
            return Response('Уже существует', status=status.HTTP_400_BAD_REQUEST)
        recipe = get_object_or_404(Recipe, id=pk)
        model.objects.create(
            user=self.get_user,
            recipe=recipe
        )
        serializer = RecipeSerializer(recipe)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @property
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
        detail=True,
        methods=['get', 'delete'],
    )
    def favourite(self, pk):
        self.get_or_delete(pk, Favourite)

    @action(methods=['get'], detail=False)
    def download_shopping_cart(self):
        if not self.get_user.carts.exists():
            return Response('Корзина пуста', status=status.HTTP_400_BAD_REQUEST)
        name = f'{self.get_user}_shopping_list'
        ingredients = IngredientAmount.objects.filter(
            recipe__in=self.get_user.carts.values('id')
        ).values(
            ingredient=F('ingredients__name'),
            measure=F('ingredients__measurement_unit')
        ).annotate(amount=Sum('amount'))
        response = HttpResponse(
            create_cart(
                ingredients,
                self.get_user,
            ),
            content_type='text.txt; charset=utf-8'
        )
        response['Content-Disposition'] = f'attachment; filename={name}'
        return response


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    pagination_class = PagePagination

    @property
    def get_user(self):
        return self.request.user

    @property
    def get_author(self, id):
        return get_object_or_404(User, id=id)

    @action(methods=['get'],
            detail=False,
            url_path='me',
            url_name='me'
            )
    def me(self, request):
        serializer = UserSerializer(request.user, partial=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=False)
    def subscriptions(self, request):
        serializer = FollowSerializer(
            self.paginate_queryset(
                Follow.objects.filter(user=self.get_user)
            ),
            many=True,
            context={'request': request}
        )
        return self.get_paginated_response(serializer.data)

    @action(
        detail=True,
        methods=['post', 'delete'],
    )
    def subscribe(self, id):
        if self.request.method == 'DELETE':
            if self.get_user == self.get_author(id) or not Follow.objects.filter(
                    user=self.get_user,
                    author=self.get_author(id)
            ).exists():
                return Response('', status=status.HTTP_400_BAD_REQUEST)
            Follow.objects.filter(
                user=self.get_user,
                author=self.get_author(id)
            ).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            if self.get_user == self.get_author(id) or Follow.objects.filter(
                    user=self.get_user,
                    author=self.get_author(id)
            ).exists():
                return Response('', status=status.HTTP_400_BAD_REQUEST)
            serializer = FollowSerializer(
                Follow.objects.create(
                    user=self.get_user,
                    aurhor=self.get_author(id)
                ),
                context={'request': self.request}
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)

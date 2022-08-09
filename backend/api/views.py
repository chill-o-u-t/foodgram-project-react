from django.db.models import F, Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from requests import Response
from rest_framework import mixins, filters, viewsets, status
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
#from .permissions import Admin
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
    #permission_classes = (IsAuthenticated,)
    serializer_class = TagSerializer
    filter_backends = (filters.SearchFilter,)


class IngredientsViewSet(viewsets.ModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientsSerializer
    filter_backends = (filters.SearchFilter,)


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    pagination_class = LimitOffsetPagination

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
            return Response('', status=status.HTTP_400_BAD_REQUEST)
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
                '', status=status.HTTP_400_BAD_REQUEST
            )
        obj.delete()
        return Response('', status=status.HTTP_204_NO_CONTENT)

    def download_shopping_cart(self):
        pass

    @action(
        detail=True,
        methods=['get', 'delete'],
    )
    def favourite(self, pk):
        self.get_or_delete(pk, Favourite)

    @action(methods=['get'], detail=True)
    def download_shopping_cart(self):
        if not self.get_user.carts.exists():
            return Response('', status=status.HTTP_400_BAD_REQUEST)
        name = f'{self.get_user}_shopping_list'
        response = HttpResponse(
            create_cart(
                IngredientAmount.objects.filter(
                    recipe__cart__user=self.get_user
                ).values_list(
                 'ingredient__name',
                 'ingredient__measurement_unit',
                 'amount'
                ),
                name
            ),
            content_type='application/pdf'
        )
        response['Content-Disposition'] = f'attachment; filename={name}'
        return response


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    filter_backends = (filters.SearchFilter,)
    search_fields = ('username',)
    pagination_class = LimitOffsetPagination
    lookup_field = 'username'

    @property
    def get_user(self):
        return self.request.user

    @property
    def get_author(self, id):
        return get_object_or_404(User, id=id)

    @action(methods=['get'], detail=True)
    def me(self, request):
        serializer = UserSerializer(request.user, partial=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(methods=['get'], detail=True )
    def subscribe(self):
        serializer = FollowSerializer(self.request.user, partical=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True)
    def add_subscribe(self, id):
        if self.get_user == self.get_author(id) or Follow.objects.filter(
                user=self.get_user,
                author=self.get_author(id)
        ).exists():
            return Response('', status=status.HTTP_400_BAD_REQUEST)
        serializer = FollowSerializer(
            Follow.objects.create(
                user=self.get_user,
                aurhor=self.get_author
            ),
            context={'request': self.request}
        )
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @subscribe.mapping.delete
    def del_subscribe(self, id):
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





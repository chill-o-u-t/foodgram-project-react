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
    RecipeSerializer
)
#from .permissions import Admin
from recipes.models import (
    User,
    Tag,
    Ingredients,
    Recipe,
    Cart,
    Favourite
)


class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    #permission_classes = (IsAuthenticated,)
    serializer_class = TagSerializer
    filter_backends = (filters.SearchFilter,)


class IngredientsViewSet(viewsets.ModelViewSet):
    queryset = Ingredients.objects.all()
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


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    #permission_classes = (Admin,)
    serializer_class = UserSerializer
    filter_backends = (filters.SearchFilter,)
    search_fields = ('username',)
    pagination_class = LimitOffsetPagination
    lookup_field = 'username'

    @property
    def get_user(self):
        return self.request.user

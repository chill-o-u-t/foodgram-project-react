from rest_framework import mixins, filters, viewsets
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import IsAuthenticated

from .serializers import (
    FavouriteSerializer,
    UserSerializer
)
from .permissions import Admin
from recipes.models import (
    User
)


class FavouriteListCreateMixin(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet,
):
    permission_classes = (IsAuthenticated,)
    filter_backends = (filters.SearchFilter,)
    pagination_class = LimitOffsetPagination


class FavouriteViewSet(
    FavouriteListCreateMixin
):
    serializer_class = FavouriteSerializer
    search_fields = ('=author__username',)

    @property
    def get_queryset(self):
        return self.request.user.favourites.all()

    @property
    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    permission_classes = (Admin,)
    serializer_class = UserSerializer
    filter_backends = (filters.SearchFilter,)
    search_fields = ('username',)
    pagination_class = LimitOffsetPagination
    lookup_field = 'username'

    def create(self, request, *args, **kwargs):
        pass




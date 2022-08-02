from rest_framework import mixins, filters, viewsets

from api.serializers import (
    FollowSerializer,
    FavouriteSerializer
)
from rest_framework.permissions import IsAuthenticated

from backend.api.serializers import


class FollowFavouriteListCreateMixin(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet,
):
    permission_classes = (IsAuthenticated,)
    filter_backends = (filters.SearchFilter,)


class FollowViewSet(
    FollowFavouriteListCreateMixin
):
    serializer_class = FollowSerializer
    search_fields = ('=user__username', '=following__username')

    @property
    def get_queryset(self):
        return self.request.user.follower.all()

    @property
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class FavouriteViewSet(
    FollowFavouriteListCreateMixin
):
    serializer_class = FavouriteSerializer
    search_fields = ('=author__username',)

    @property
    def get_queryset(self):
        return self.request.user.favourites.all()

    @property
    def perform_create(self, serializer):
        serializer.save(author=self.request.user)



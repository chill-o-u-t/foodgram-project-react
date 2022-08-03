from rest_framework.routers import SimpleRouter
from django.urls import path, include

from .views import (
    FollowViewSet,
    FavouriteViewSet
)

router_v1 = SimpleRouter()
router_v1.register(
    'follows',
    FollowViewSet,
    basename='follows'
)
router_v1.register(
    'favourites',
    FavouriteViewSet,
    basename='favourites'
)


urlpatterns = [
    path('/', include(router_v1.urls)),
    path('auth/', include('djoser.urls')),
    path('auth/', include('djoser.urls.jwt')),
]

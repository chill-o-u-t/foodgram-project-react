from rest_framework.routers import SimpleRouter
from django.urls import path, include

from .views import (
    TagViewSet,
    IngredientsViewSet,
    RecipeViewSet,
    UserViewSet
)

router_v1 = SimpleRouter()
router_v1.register(
    'tags',
    TagViewSet,
    basename='tags'
)
router_v1.register(
    'recipes',
    RecipeViewSet,
    basename='recipes'
)
router_v1.register(
    'ingredients',
    IngredientsViewSet,
    basename='ingredients'
)
router_v1.register(
    'users',
    UserViewSet,
    basename='users'
)


urlpatterns = [
    path('', include(router_v1.urls)),
    path('auth/', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
]


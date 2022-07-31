from rest_framework.routers import SimpleRouter
from django.urls import path, include

router_v1 = SimpleRouter()


urlpatterns = [
    path('auth/', include('djoser.urls')),
    path('auth/', include('djoser.urls.jwt')),
]

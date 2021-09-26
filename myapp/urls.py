from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import MessagesViewSet


router = DefaultRouter()
router.register('messages', MessagesViewSet)

urlpatterns = [
    path('api/', include(router.urls)),
]

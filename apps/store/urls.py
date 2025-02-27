from rest_framework.routers import DefaultRouter
from django.urls import path,include
from .views import *


router = DefaultRouter()
router.register(r'categories', CategoryViewSet, basename='category')
router.register(r'locations', LocationViewSet, basename='location')
router.register(r'product-group', ProductGroupViewSet, basename='product-group')
router.register(r'products', ProductViewSet, basename='product')
router.register(r'store-requests', StoreRequestViewSet, basename='store-request')
router.register(r'daily-entry', StoreDailyEntryViewSet, basename='daily-entry')


urlpatterns = [
    path('', include(router.urls)),
    path('test/', Test.as_view()),
]
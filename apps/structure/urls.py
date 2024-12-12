from rest_framework.routers import DefaultRouter
from django.urls import path,include
from .views import *


router = DefaultRouter()
router.register(r'zones', ZoneViewSet, basename='zone')
router.register(r'districts', DistrictViewSet, basename='district')
router.register(r'landmarks', LandmarkViewSet, basename='landmark')
router.register(r'junctions', JunctionViewSet, basename='junction')
router.register(r'poles', PoleViewSet, basename='pole')
router.register(r'equipments', EquipmentViewSet, basename='equipment')

urlpatterns = [
    path('', include(router.urls)),
    path('test/', Test.as_view()),
    path('logs/', FilterLogsByDate.as_view()),
]
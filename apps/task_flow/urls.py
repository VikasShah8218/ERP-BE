from rest_framework.routers import DefaultRouter
from django.urls import path,include
from .views import *


router = DefaultRouter()
router.register(r'tasks', TaskAssignViewSet, basename='taskassign')
router.register(r'get-users-with-landmarks', UsersWithLandmarksViewSet, basename='users-with-landmarks')
router.register(r'users-with-landmarks', AssosiatedUsersLandmarkViewSet, basename='users-with-landmark')

urlpatterns = [
    path('', include(router.urls)),
    path('test/', Test.as_view()),
    # path('logs/', FilterLogsByDate.as_view()),
]
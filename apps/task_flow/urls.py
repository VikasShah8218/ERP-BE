from rest_framework.routers import DefaultRouter
from django.urls import path,include
from .views import *


router = DefaultRouter()
router.register(r'tasks', TaskAssignViewSet, basename='taskassign')
router.register(r'get-users-with-landmarks', UsersWithLandmarksViewSet, basename='users-with-landmarks')
router.register(r'users-with-landmarks', AssosiatedUsersLandmarkViewSet, basename='users-with-landmark')
router.register(r'task-re-allocations', TaskReAllocationViewSet, basename='task-re-allocation')
router.register(r'task-landmark-completions', TaskLandmarkCompleteViewSet, basename='task-landmark-completions')
router.register(r'task-media', TaskMediaViewSet, basename='task-media')


urlpatterns = [
    path('', include(router.urls)),
    path('test/', Test.as_view()),
]
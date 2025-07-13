from rest_framework.routers import DefaultRouter
from django.urls import path, include
from .views import *


router = DefaultRouter()
router.register(r'department', DepartmentModelAPI, basename='department')

urlpatterns = [
    path('', include(router.urls)),
    path('test/', Test.as_view()),
    path('login/', LoginUser.as_view()),    
    path('logout/', LogoutView.as_view()),
    path('create-admin/', RegisterAdmin.as_view({'post': 'create'})),
    path('create-users/', CreateUserByAdmin.as_view({'post': 'create'})),
    path('get-all-user/',GetAllUsersByAdmin.as_view({'get': 'list'})),
    path('update-user/<int:id>/', UpdateUserDetailsByAdmin.as_view()),
    path('reset-password-by-user/', ResetPasswordByUser.as_view()),
    path('reset-password-by-admin/<int:id>/', ResetPasswordByAdmin.as_view()),
    path('validate-token/' , ValidateTokenAPIView.as_view()),
    path('user/<int:user_id>/', GetUserById.as_view(), name='get_user_by_id'),
]
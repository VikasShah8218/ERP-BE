from django.contrib import admin
from django.urls import path , include
# from rest_framework_simplejwt.views import (
#     TokenObtainPairView,
#     TokenRefreshView,
#     TokenVerifyView
# )
# for dubug only ---------------
from django.conf import settings
from django.conf.urls.static import static
# -----------------------------

# jwt_token_url_patterns = [
#     path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
#     path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
#     path('api/token/verify/', TokenVerifyView.as_view(), name='token_verify'),
# ]

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/' , include(('apps.accounts.urls'))),
    path('structure/' , include(('apps.structure.urls'))),
    path('task_flow/' , include(('apps.task_flow.urls'))),
    # path('gadgets/' , include(('apps.gadgets.urls'))),
    # path('passes/' , include(('apps.passes.urls'))),
    # path('face_recognition/' , include(('apps.face_recognition.urls'))),
    # path('reports/' , include(('apps.reports.urls'))),
    # path('dashboard/' , include(('apps.dashboard.urls'))),
    

]# +jwt_token_url_patterns

# for dubug only ---------------
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
# -----------------------------
from django.contrib import admin
from django.urls import path , include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/' , include(('apps.accounts.urls'))),
    path('structure/' , include(('apps.structure.urls'))),
    path('task_flow/' , include(('apps.task_flow.urls'))),
    path('store/' , include(('apps.store.urls'))),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
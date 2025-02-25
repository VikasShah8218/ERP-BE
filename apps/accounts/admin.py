from django.contrib import admin
from .models import User ,Department, CustomPermission

admin.site.register(User)
admin.site.register(Department)

@admin.register(CustomPermission)
class CustomPermissionAdmin(admin.ModelAdmin):
    list_display = ["codename", "name", "description"]
    search_fields = ["codename", "name"]
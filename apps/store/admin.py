from django.contrib import admin
from .models import Category,Group,Location,Product,StoreRequest,Approval

admin.site.register(Category)
admin.site.register(Group)
admin.site.register(Location)
admin.site.register(Product)
admin.site.register(StoreRequest)
admin.site.register(Approval)
from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.


class User(AbstractUser):
    class Meta:
        db_table = 'auth_user'

    USER_TYPES = {
        'Admin': 'Admin',
        'District_Admin': 'District_Admin',
        'Employee': 'Employee',
    }

    user_type = models.CharField(max_length=255, choices=USER_TYPES, default=USER_TYPES['Employee'])
    phone = models.CharField(max_length=255, null=True, blank=True)
    address = models.TextField(null=True)
    # employee_code = models.CharField(max_length=255, unique=True, null=False)
    work_location = models.TextField(null=True)
    department = models.CharField(max_length=255, null=True)
    created_by = models.ForeignKey("self", on_delete=models.CASCADE, null=True, related_name="created_users")
    updated_by = models.ForeignKey("self", on_delete=models.CASCADE, null=True, related_name="updated_users")
    client_id = models.CharField(max_length=255,null=True,blank=True)
    image = models.TextField(null=True, blank=True)
    is_present = models.BooleanField(default=True)
    created_on = models.DateTimeField(auto_now_add=True, null=True)
    updated_on = models.DateTimeField(auto_now=True)

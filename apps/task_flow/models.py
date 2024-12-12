from django.db import models
from apps.structure.models import Landmark
from apps.accounts.models import User


class TaskAssign(models.Model):
    class Meta:
        db_table = 'tbl_task_assign'

    name = models.CharField(max_length=255)
    landmark = models.ForeignKey(Landmark, on_delete=models.CASCADE, related_name='task_assign')
    estimate_ex_date = models.DateTimeField(null=True, blank=True)
    note = models.TextField(blank=True, null=True)
    assigned_users = models.ManyToManyField(User, related_name='assigned_tasks', blank=True)
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, null=True, related_name="task_created_by")
    updated_by = models.ForeignKey(User, on_delete=models.CASCADE, null=True, related_name="task_updated_by")
    is_started = models.BooleanField(null=True, blank=True)
    started_on = models.DateTimeField(null=True,blank=True)
    is_complete = models.BooleanField(null=True, blank=True)
    completed_on = models.DateTimeField(null=True,blank=True)
    conversation = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name
    
class AssosiatedUsersLandmark(models.Model):
    class Meta():
        db_table = "tbl_associated_users_landmark"
    landmark = models.ForeignKey(Landmark,on_delete=models.CASCADE, related_name='associated_landmark')
    user = models.ForeignKey(User,on_delete=models.CASCADE, related_name='associated_user')
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, null=True, related_name="associated_created_by")
    updated_by = models.ForeignKey(User, on_delete=models.CASCADE, null=True, related_name="associated_updated_by")
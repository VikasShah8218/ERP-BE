from django.db import models
from apps.structure.models import Landmark
from apps.accounts.models import User

 
class TaskAssign(models.Model):
    class Meta:
        db_table = 'tbl_task_assign'

    name = models.CharField(max_length=255)
    landmarks = models.ManyToManyField(Landmark, related_name='task_assignments')
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

class TaskLandmarkComplete(models.Model):
    class Meta:
        db_table = "tbl_task_landmark_complete"
        unique_together = ('task', 'landmark')  # Ensure a task-landmark pair is unique

    task = models.ForeignKey(
        'TaskAssign', 
        on_delete=models.CASCADE, 
        related_name='task_landmark_completions'
    )
    landmark = models.ForeignKey(
        Landmark, 
        on_delete=models.CASCADE, 
        related_name='landmark_task_completions'
    )
    created_by = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        null=True, 
        related_name='task_landmark_completions_created'
    )
    updated_by = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        null=True, 
        related_name='task_landmark_completions_updated'
    )

    
    is_complete = models.BooleanField(default=False)  # Field to track completion
    created_on = models.DateTimeField(auto_now_add=True)  # Auto add creation timestamp
    updated_on = models.DateTimeField(auto_now=True)  # Auto update timestamp

    def __str__(self):
        return f"Task: {self.task.name}, Landmark: {self.landmark.name}, Completed: {self.is_complete}"

class TaskReAllocation(models.Model):
    class Meta:
        db_table = "tbl_task_re_allocation"

    task = models.ForeignKey("TaskAssign", on_delete=models.CASCADE, related_name="re_allocations")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="re_allocations_made")  
    re_allocate_to = models.ForeignKey(User, on_delete=models.CASCADE, related_name="re_allocated_tasks")  
    message = models.TextField(null=True, blank=True) 
    created_on = models.DateTimeField(auto_now_add=True) 
    updated_on = models.DateTimeField(auto_now=True) 

    def __str__(self):
        return f"Task {self.task.name} re-allocated to {self.re_allocate_to.username}"

class AssosiatedUsersLandmark(models.Model):
    class Meta():
        db_table = "tbl_associated_users_landmark"
    landmark = models.ForeignKey(Landmark,on_delete=models.CASCADE, related_name='associated_landmark')
    user = models.ForeignKey(User,on_delete=models.CASCADE, related_name='associated_user')
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, null=True, related_name="associated_created_by")
    updated_by = models.ForeignKey(User, on_delete=models.CASCADE, null=True, related_name="associated_updated_by")

class TaskMedia(models.Model):
    class Meta:
        db_table = "tbl_task_media"

    task = models.ForeignKey(TaskAssign, on_delete=models.CASCADE, related_name="task_media")  # Link to TaskAssign
    file_type = models.CharField(max_length=10)  # Type of file
    file = models.FileField(upload_to="task_media/")  # File field to store the media
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name="media_created_by")
    updated_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name="media_updated_by",null=True)

    def __str__(self):
        return f"{self.task.name} - {self.file_type} ({self.file.name})"

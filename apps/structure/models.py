from django.db import models

class Zone(models.Model):
    class Meta:
        db_table = 'tbl_zone'
    name = models.CharField(max_length=255)
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)
    note = models.TextField(blank=True,null=True)
    is_delete = models.BooleanField(null=True,blank=True,default=False)

    def __str__(self):
        return self.name

class District(models.Model):
    class Meta:
        db_table = 'tbl_district'
    meta_id = models.CharField(max_length=255,null=False,blank=False,unique=True)
    zone = models.ForeignKey(Zone, on_delete=models.CASCADE, related_name='districts')
    name = models.CharField(max_length=255)
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)
    note = models.TextField(blank=True,null=True)
    is_delete = models.BooleanField(null=True,blank=True,default=False)


    def __str__(self):
        return self.name

class Landmark(models.Model):
    class Meta:
        db_table = 'tbl_landmark'
    meta_id = models.CharField(max_length=255,null=False,blank=False,unique=True)
    district = models.ForeignKey(District, on_delete=models.CASCADE, related_name='landmarks')
    name = models.CharField(max_length=255)
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)
    note = models.TextField(blank=True,null=True)
    is_delete = models.BooleanField(null=True,blank=True,default=False)


    def __str__(self):
        return self.name

class Junction(models.Model):
    class Meta:
        db_table = 'tbl_junction'
    meta_id = models.CharField(max_length=255,null=False,blank=False,unique=True)
    landmark = models.ForeignKey(Landmark, on_delete=models.CASCADE, related_name='junctions')
    name = models.CharField(max_length=255)
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)
    note = models.TextField(blank=True,null=True)
    is_delete = models.BooleanField(null=True,blank=True,default=False)


    def __str__(self):
        return self.name

class Pole(models.Model):
    class Meta:
        db_table = 'tbl_pole'
    meta_id = models.CharField(max_length=255,null=False,blank=False,unique=True)
    junction = models.ForeignKey(Junction, on_delete=models.CASCADE, related_name='poles')
    name = models.CharField(max_length=255)
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)
    note = models.TextField(blank=True,null=True)
    is_delete = models.BooleanField(null=True,blank=True,default=False)


    def __str__(self):
        return self.name

class Equipment(models.Model):
    class Meta:
        db_table = 'tbl_equipment'
    meta_id = models.CharField(max_length=255,null=False,blank=False,unique=True)
    pole = models.ForeignKey(Pole, on_delete=models.CASCADE, related_name='equipments')
    name = models.CharField(max_length=255)
    type = models.CharField(max_length=255)
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)
    note = models.TextField(blank=True,null=True)
    is_delete = models.BooleanField(null=True,blank=True,default=False)


    def __str__(self):
        return f"{self.name} ({self.type})"

# -----------------------------------------Log Model------------------------------------------#

class ZoneLog(models.Model):
    class Meta:
        db_table = 'tbl_log_zone'
    zone = models.ForeignKey('Zone', on_delete=models.CASCADE, related_name='logs',null=True)
    previous_values = models.JSONField(default=dict)  # Stores the previous state of the zone
    current_values = models.JSONField(default=dict)   # Stores the current state of the zone
    action = models.CharField(max_length=10, choices=[('create', 'Create'), ('update', 'Update'), ('delete', 'Delete')])
    timestamp = models.DateTimeField(auto_now_add=True)  # Automatically set the timestamp when the log is created
    structure_count = models.JSONField(default=dict,null=True,blank=True)

    def __str__(self):
        return f"ZoneLog {self.zone.id} - {self.action} - {self.timestamp}"
        

class DistrictLog(models.Model):
    class Meta:
        db_table = 'tbl_log_district'
    district = models.ForeignKey('District', on_delete=models.CASCADE, related_name='logs')
    previous_values = models.JSONField(default=dict)  # Stores the previous state of the district
    current_values = models.JSONField(default=dict)   # Stores the current state of the district
    action = models.CharField(max_length=10, choices=[('create', 'Create'), ('update', 'Update'), ('delete', 'Delete')])
    timestamp = models.DateTimeField(auto_now_add=True)  # Automatically set the timestamp when the log is created
    structure_count = models.JSONField(default=dict,null=True,blank=True)

    def __str__(self):
        return f"DistrictLog {self.district.id} - {self.action} - {self.timestamp}"

class LandmarkLog(models.Model):
    class Meta:
        db_table = 'tbl_log_landmark'
    landmark = models.ForeignKey('Landmark', on_delete=models.CASCADE, related_name='logs')
    previous_values = models.JSONField(default=dict)  # Stores the previous state of the landmark
    current_values = models.JSONField(default=dict)   # Stores the current state of the landmark
    action = models.CharField(max_length=10, choices=[('create', 'Create'), ('update', 'Update'), ('delete', 'Delete')])
    timestamp = models.DateTimeField(auto_now_add=True)  # Automatically set the timestamp when the log is created
    structure_count = models.JSONField(default=dict,null=True,blank=True)

    def __str__(self):
        return f"LandmarkLog {self.landmark.id} - {self.action} - {self.timestamp}"

class JunctionLog(models.Model):
    class Meta:
        db_table = 'tbl_log_junction'
    junction = models.ForeignKey('Junction', on_delete=models.CASCADE, related_name='logs')
    previous_values = models.JSONField(default=dict)  # Stores the previous state of the junction
    current_values = models.JSONField(default=dict)   # Stores the current state of the junction
    action = models.CharField(max_length=10, choices=[('create', 'Create'), ('update', 'Update'), ('delete', 'Delete')])
    timestamp = models.DateTimeField(auto_now_add=True)  # Automatically set the timestamp when the log is created
    structure_count = models.JSONField(default=dict,null=True,blank=True)

    def __str__(self):
        return f"JunctionLog {self.junction.id} - {self.action} - {self.timestamp}"

class PoleLog(models.Model):
    class Meta:
        db_table = 'tbl_log_pole'
    pole = models.ForeignKey('Pole', on_delete=models.CASCADE, related_name='logs')
    previous_values = models.JSONField(default=dict)  # Stores the previous state of the pole
    current_values = models.JSONField(default=dict)   # Stores the current state of the pole
    action = models.CharField(max_length=10, choices=[('create', 'Create'), ('update', 'Update'), ('delete', 'Delete')])
    timestamp = models.DateTimeField(auto_now_add=True)  # Automatically set the timestamp when the log is created
    structure_count = models.JSONField(default=dict,null=True,blank=True)

    def __str__(self):
        return f"PoleLog {self.pole.id} - {self.action} - {self.timestamp}"

class EquipmentLog(models.Model):
    class Meta:
        db_table = 'tbl_log_equipment'
    equipment = models.ForeignKey('Equipment', on_delete=models.CASCADE, related_name='logs')
    previous_values = models.JSONField(default=dict)  # Stores the previous state of the equipment
    current_values = models.JSONField(default=dict)   # Stores the current state of the equipment
    action = models.CharField(max_length=10, choices=[('create', 'Create'), ('update', 'Update'), ('delete', 'Delete')])
    timestamp = models.DateTimeField(auto_now_add=True)  # Automatically set the timestamp when the log is created
    structure_count = models.JSONField(default=dict,null=True,blank=True)

    def __str__(self):
        return f"EquipmentLog {self.equipment.id} - {self.action} - {self.timestamp}"

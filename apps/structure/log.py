from .models import Zone,District, Landmark, Junction, Pole, Equipment, ZoneLog , DistrictLog , LandmarkLog , JunctionLog, PoleLog , EquipmentLog
from django.db.models.signals import pre_save, post_save, pre_delete
from django.dispatch import receiver
from django.utils import timezone
from django.db.models import Model
from django.db.models import Count
import datetime

def get_model_data(instance):
    data = {}
    for field in instance._meta.fields:
        value = getattr(instance, field.name)
        if isinstance(value, (Model)):
            data[field.name] = value.id
        else:       
            data[field.name] = value
    return data


def convert_datetimes_to_string(data):
    """Helper function to convert datetime fields to ISO string format"""
    for key, value in data.items():
        if isinstance(value, (timezone.datetime, datetime.date)):
            data[key] = value.isoformat()  # Convert datetime to ISO format string
    return data

@receiver(pre_save, sender=Zone)
def zone_pre_save(sender, instance, **kwargs):
    if instance.pk:
        previous = Zone.objects.get(pk=instance.pk)
        previous_values = get_model_data(previous)
        current_values = get_model_data(instance)

        previous_values = convert_datetimes_to_string(previous_values)
        current_values = convert_datetimes_to_string(current_values)
        counts = {
            "zones": Zone.objects.filter(is_delete=False).aggregate(count=Count('id'))['count'],
            "districts": District.objects.filter(is_delete=False).aggregate(count=Count('id'))['count'],
            "landmarks": Landmark.objects.filter(is_delete=False).aggregate(count=Count('id'))['count'],
            "poles": Pole.objects.filter(is_delete=False).aggregate(count=Count('id'))['count'],
            "equipments": Equipment.objects.filter(is_delete=False).aggregate(count=Count('id'))['count'],
        }
       
        if instance.is_delete:
            log = ZoneLog.objects.create(
                zone=instance,
                action='delete',
                previous_values=previous_values,
                current_values=current_values,
                structure_count = counts
            )
        else:
            log = ZoneLog.objects.create(
                zone=instance,
                action='update' if previous_values["is_delete"] == current_values["is_delete"] else "undelete" ,
                previous_values=previous_values,
                current_values=current_values,
                structure_count = counts
            )
        instance._log_id = log.id
        
@receiver(post_save, sender=Zone)
def zone_post_save(sender, instance,created, **kwargs):
    counts = {
        "zones": Zone.objects.filter(is_delete=False).aggregate(count=Count('id'))['count'],
        "districts": District.objects.filter(is_delete=False).aggregate(count=Count('id'))['count'],
        "landmarks": Landmark.objects.filter(is_delete=False).aggregate(count=Count('id'))['count'],
        "poles": Pole.objects.filter(is_delete=False).aggregate(count=Count('id'))['count'],
        "equipments": Equipment.objects.filter(is_delete=False).aggregate(count=Count('id'))['count'],
    }
    if created:
        current_values = get_model_data(instance)
        current_values = convert_datetimes_to_string(current_values)
        ZoneLog.objects.create(
            zone=instance,
            action='create',
            previous_values={},
            current_values=current_values,
            structure_count = counts
        )

    if hasattr(instance, '_log_id'):
        pre_log = ZoneLog.objects.get(id=instance._log_id)
        pre_log.structure_count = counts
        pre_log.save()

# ---------------------------------district-------------------------------

@receiver(pre_save, sender=District)
def district_pre_save(sender, instance, **kwargs):
    if instance.pk:
        previous = District.objects.get(pk=instance.pk)
        previous_values = get_model_data(previous)
        current_values = get_model_data(instance)

        previous_values = convert_datetimes_to_string(previous_values)
        current_values = convert_datetimes_to_string(current_values)
        counts = {
            "zones": Zone.objects.filter(is_delete=False).aggregate(count=Count('id'))['count'],
            "districts": District.objects.filter(is_delete=False).aggregate(count=Count('id'))['count'],
            "landmarks": Landmark.objects.filter(is_delete=False).aggregate(count=Count('id'))['count'],
            "poles": Pole.objects.filter(is_delete=False).aggregate(count=Count('id'))['count'],
            "equipments": Equipment.objects.filter(is_delete=False).aggregate(count=Count('id'))['count'],
        }
        if instance.is_delete:
            log = DistrictLog.objects.create(
                district=instance,
                action='delete',
                previous_values=previous_values,
                current_values=current_values,
                structure_count = counts
            )
        else:
            action = 'update' if previous_values["is_delete"] == current_values["is_delete"] else 'undelete'
            log = DistrictLog.objects.create(
                district=instance,
                action=action,
                previous_values=previous_values,
                current_values=current_values,
                structure_count = counts
            )
        instance._log_id = log.id
        
@receiver(post_save, sender=District)
def district_post_save(sender, instance, created, **kwargs):
    counts = {
        "zones": Zone.objects.filter(is_delete=False).aggregate(count=Count('id'))['count'],
        "districts": District.objects.filter(is_delete=False).aggregate(count=Count('id'))['count'],
        "landmarks": Landmark.objects.filter(is_delete=False).aggregate(count=Count('id'))['count'],
        "poles": Pole.objects.filter(is_delete=False).aggregate(count=Count('id'))['count'],
        "equipments": Equipment.objects.filter(is_delete=False).aggregate(count=Count('id'))['count'],
    }
    if created:
        current_values = get_model_data(instance)
        current_values = convert_datetimes_to_string(current_values)
        DistrictLog.objects.create(
            district=instance,
            action='create',
            previous_values={},
            current_values=current_values,
                structure_count = counts
        )
    if hasattr(instance, '_log_id'):
        pre_log = DistrictLog.objects.get(id=instance._log_id)
        pre_log.structure_count = counts
        pre_log.save()

# ---------------------------------landMark-------------------------------

@receiver(pre_save, sender=Landmark)
def landmark_pre_save(sender, instance, **kwargs):
    if instance.pk:
        previous = Landmark.objects.get(pk=instance.pk)
        previous_values = get_model_data(previous)
        current_values = get_model_data(instance)

        previous_values = convert_datetimes_to_string(previous_values)
        current_values = convert_datetimes_to_string(current_values)
        counts = {
            "zones": Zone.objects.filter(is_delete=False).aggregate(count=Count('id'))['count'],
            "districts": District.objects.filter(is_delete=False).aggregate(count=Count('id'))['count'],
            "landmarks": Landmark.objects.filter(is_delete=False).aggregate(count=Count('id'))['count'],
            "poles": Pole.objects.filter(is_delete=False).aggregate(count=Count('id'))['count'],
            "equipments": Equipment.objects.filter(is_delete=False).aggregate(count=Count('id'))['count'],
        }
        if instance.is_delete:
            log = LandmarkLog.objects.create(
                landmark=instance,
                action='delete',
                previous_values=previous_values,
                current_values=current_values,
                structure_count = counts
            )
        else:
            action = 'update' if previous_values["is_delete"] == current_values["is_delete"] else 'undelete'
            log = LandmarkLog.objects.create(
                landmark=instance,
                action=action,
                previous_values=previous_values,
                current_values=current_values,
                structure_count = counts
            )
        instance._log_id = log.id

@receiver(post_save, sender=Landmark)
def landmark_post_save(sender, instance, created, **kwargs):
    counts = {
        "zones": Zone.objects.filter(is_delete=False).aggregate(count=Count('id'))['count'],
        "districts": District.objects.filter(is_delete=False).aggregate(count=Count('id'))['count'],
        "landmarks": Landmark.objects.filter(is_delete=False).aggregate(count=Count('id'))['count'],
        "poles": Pole.objects.filter(is_delete=False).aggregate(count=Count('id'))['count'],
        "equipments": Equipment.objects.filter(is_delete=False).aggregate(count=Count('id'))['count'],
    }
    if created:
        current_values = get_model_data(instance)
        current_values = convert_datetimes_to_string(current_values)
        LandmarkLog.objects.create(
            landmark=instance,
            action='create',
            previous_values={},
            current_values=current_values,
                structure_count = counts
        )
    
    if hasattr(instance, '_log_id'):
        pre_log = LandmarkLog.objects.get(id=instance._log_id)
        pre_log.structure_count = counts
        pre_log.save()

# ---------------------------------Junction-------------------------------

@receiver(pre_save, sender=Junction)
def junction_pre_save(sender, instance, **kwargs):
    if instance.pk:
        previous = Junction.objects.get(pk=instance.pk)
        previous_values = get_model_data(previous)
        current_values = get_model_data(instance)

        previous_values = convert_datetimes_to_string(previous_values)
        current_values = convert_datetimes_to_string(current_values)
        counts = {
            "zones": Zone.objects.filter(is_delete=False).aggregate(count=Count('id'))['count'],
            "districts": District.objects.filter(is_delete=False).aggregate(count=Count('id'))['count'],
            "landmarks": Landmark.objects.filter(is_delete=False).aggregate(count=Count('id'))['count'],
            "poles": Pole.objects.filter(is_delete=False).aggregate(count=Count('id'))['count'],
            "equipments": Equipment.objects.filter(is_delete=False).aggregate(count=Count('id'))['count'],
        }
        if instance.is_delete:
            log = JunctionLog.objects.create(
                junction=instance,
                action='delete',
                previous_values=previous_values,
                current_values=current_values,
                structure_count = counts
            )
        else:
            action = 'update' if previous_values["is_delete"] == current_values["is_delete"] else 'undelete'
            log = JunctionLog.objects.create(
                junction=instance,
                action=action,
                previous_values=previous_values,
                current_values=current_values,
                structure_count = counts
            )
        instance._log_id = log.id

@receiver(post_save, sender=Junction)
def junction_post_save(sender, instance, created, **kwargs):
    counts = {
        "zones": Zone.objects.filter(is_delete=False).aggregate(count=Count('id'))['count'],
        "districts": District.objects.filter(is_delete=False).aggregate(count=Count('id'))['count'],
        "landmarks": Landmark.objects.filter(is_delete=False).aggregate(count=Count('id'))['count'],
        "poles": Pole.objects.filter(is_delete=False).aggregate(count=Count('id'))['count'],
        "equipments": Equipment.objects.filter(is_delete=False).aggregate(count=Count('id'))['count'],
    }
    if created:
        current_values = get_model_data(instance)
        current_values = convert_datetimes_to_string(current_values)
        JunctionLog.objects.create(
            junction=instance,
            action='create',
            previous_values={},
            current_values=current_values,
                structure_count = counts
        )
    
    if hasattr(instance, '_log_id'):
        pre_log = JunctionLog.objects.get(id=instance._log_id)
        pre_log.structure_count = counts
        pre_log.save()

# ---------------------------------Poles-------------------------------

@receiver(pre_save, sender=Pole)
def pole_pre_save(sender, instance, **kwargs):
    if instance.pk:
        previous = Pole.objects.get(pk=instance.pk)
        previous_values = get_model_data(previous)
        current_values = get_model_data(instance)

        previous_values = convert_datetimes_to_string(previous_values)
        current_values = convert_datetimes_to_string(current_values)
        counts = {
            "zones": Zone.objects.filter(is_delete=False).aggregate(count=Count('id'))['count'],
            "districts": District.objects.filter(is_delete=False).aggregate(count=Count('id'))['count'],
            "landmarks": Landmark.objects.filter(is_delete=False).aggregate(count=Count('id'))['count'],
            "poles": Pole.objects.filter(is_delete=False).aggregate(count=Count('id'))['count'],
            "equipments": Equipment.objects.filter(is_delete=False).aggregate(count=Count('id'))['count'],
        }
        if instance.is_delete:
            log = PoleLog.objects.create(
                pole=instance,
                action='delete',
                previous_values=previous_values,
                current_values=current_values,
                structure_count = counts
            )
        else:
            action = 'update' if previous_values["is_delete"] == current_values["is_delete"] else 'undelete'
            log = PoleLog.objects.create(
                pole=instance,
                action=action,
                previous_values=previous_values,
                current_values=current_values,
                structure_count = counts
            )
        instance._log_id = log.id

@receiver(post_save, sender=Pole)
def pole_post_save(sender, instance, created, **kwargs):
    counts = {
        "zones": Zone.objects.filter(is_delete=False).aggregate(count=Count('id'))['count'],
        "districts": District.objects.filter(is_delete=False).aggregate(count=Count('id'))['count'],
        "landmarks": Landmark.objects.filter(is_delete=False).aggregate(count=Count('id'))['count'],
        "poles": Pole.objects.filter(is_delete=False).aggregate(count=Count('id'))['count'],
        "equipments": Equipment.objects.filter(is_delete=False).aggregate(count=Count('id'))['count'],
    }
    if created:
        current_values = get_model_data(instance)
        current_values = convert_datetimes_to_string(current_values)
        PoleLog.objects.create(
            pole=instance,
            action='create',
            previous_values={},
            current_values=current_values,
            structure_count = counts
        )
    if hasattr(instance, '_log_id'):
        pre_log = PoleLog.objects.get(id=instance._log_id)
        pre_log.structure_count = counts
        pre_log.save()

# ---------------------------------equipment-------------------------------

@receiver(pre_save, sender=Equipment)
def equipment_pre_save(sender, instance, **kwargs):
    if instance.pk:
        previous = Equipment.objects.get(pk=instance.pk)
        previous_values = get_model_data(previous)
        current_values = get_model_data(instance)

        previous_values = convert_datetimes_to_string(previous_values)
        current_values = convert_datetimes_to_string(current_values)
        counts = {
            "zones": Zone.objects.filter(is_delete=False).aggregate(count=Count('id'))['count'],
            "districts": District.objects.filter(is_delete=False).aggregate(count=Count('id'))['count'],
            "landmarks": Landmark.objects.filter(is_delete=False).aggregate(count=Count('id'))['count'],
            "poles": Pole.objects.filter(is_delete=False).aggregate(count=Count('id'))['count'],
            "equipments": Equipment.objects.filter(is_delete=False).aggregate(count=Count('id'))['count'],
        }
        if instance.is_delete:
            log = EquipmentLog.objects.create(
                equipment=instance,
                action='delete',
                previous_values=previous_values,
                current_values=current_values,
                structure_count = counts
            )
        else:
            action = 'update' if previous_values["is_delete"] == current_values["is_delete"] else 'undelete'
            log = EquipmentLog.objects.create(
                equipment=instance,
                action=action,
                previous_values=previous_values,
                current_values=current_values,
                structure_count = counts
            )
        instance._log_id = log.id

@receiver(post_save, sender=Equipment)
def equipment_post_save(sender, instance, created, **kwargs):
    counts = {
        "zones": Zone.objects.filter(is_delete=False).aggregate(count=Count('id'))['count'],
        "districts": District.objects.filter(is_delete=False).aggregate(count=Count('id'))['count'],
        "landmarks": Landmark.objects.filter(is_delete=False).aggregate(count=Count('id'))['count'],
        "poles": Pole.objects.filter(is_delete=False).aggregate(count=Count('id'))['count'],
        "equipments": Equipment.objects.filter(is_delete=False).aggregate(count=Count('id'))['count'],
    }
    if created:
        current_values = get_model_data(instance)
        current_values = convert_datetimes_to_string(current_values)
        EquipmentLog.objects.create(
            equipment=instance,
            action='create',
            previous_values={},
            current_values=current_values,
                structure_count = counts
        )

    if hasattr(instance, '_log_id'):
        pre_log = EquipmentLog.objects.get(id=instance._log_id)
        pre_log.structure_count = counts
        pre_log.save()
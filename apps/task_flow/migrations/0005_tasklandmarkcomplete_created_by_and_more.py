# Generated by Django 5.1.3 on 2024-12-14 08:40

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('task_flow', '0004_remove_tasklandmarkcomplete_created_by_and_more'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='tasklandmarkcomplete',
            name='created_by',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='task_landmark_completions_created', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='tasklandmarkcomplete',
            name='updated_by',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='task_landmark_completions_updated', to=settings.AUTH_USER_MODEL),
        ),
    ]
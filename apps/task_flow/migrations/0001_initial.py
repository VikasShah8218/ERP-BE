# Generated by Django 5.1.3 on 2024-12-14 07:53

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('structure', '0003_districtlog_structure_count_and_more'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='AssosiatedUsersLandmark',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_on', models.DateTimeField(auto_now_add=True)),
                ('updated_on', models.DateTimeField(auto_now=True)),
                ('created_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='associated_created_by', to=settings.AUTH_USER_MODEL)),
                ('landmark', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='associated_landmark', to='structure.landmark')),
                ('updated_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='associated_updated_by', to=settings.AUTH_USER_MODEL)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='associated_user', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'tbl_associated_users_landmark',
            },
        ),
        migrations.CreateModel(
            name='TaskAssign',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('estimate_ex_date', models.DateTimeField(blank=True, null=True)),
                ('note', models.TextField(blank=True, null=True)),
                ('created_on', models.DateTimeField(auto_now_add=True)),
                ('updated_on', models.DateTimeField(auto_now=True)),
                ('is_started', models.BooleanField(blank=True, null=True)),
                ('started_on', models.DateTimeField(blank=True, null=True)),
                ('is_complete', models.BooleanField(blank=True, null=True)),
                ('completed_on', models.DateTimeField(blank=True, null=True)),
                ('conversation', models.TextField(blank=True, null=True)),
                ('assigned_users', models.ManyToManyField(blank=True, related_name='assigned_tasks', to=settings.AUTH_USER_MODEL)),
                ('created_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='task_created_by', to=settings.AUTH_USER_MODEL)),
                ('landmarks', models.ManyToManyField(related_name='task_assignments', to='structure.landmark')),
                ('updated_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='task_updated_by', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'tbl_task_assign',
            },
        ),
        migrations.CreateModel(
            name='TaskReAllocation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('message', models.TextField(blank=True, null=True)),
                ('created_on', models.DateTimeField(auto_now_add=True)),
                ('updated_on', models.DateTimeField(auto_now=True)),
                ('re_allocate_to', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='re_allocated_tasks', to=settings.AUTH_USER_MODEL)),
                ('task', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='re_allocations', to='task_flow.taskassign')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='re_allocations_made', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'tbl_task_re_allocation',
            },
        ),
    ]

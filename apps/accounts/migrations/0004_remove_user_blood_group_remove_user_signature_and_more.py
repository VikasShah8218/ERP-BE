# Generated by Django 5.1.3 on 2024-12-07 10:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0003_alter_user_user_type'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='user',
            name='blood_group',
        ),
        migrations.RemoveField(
            model_name='user',
            name='signature',
        ),
        migrations.AddField(
            model_name='user',
            name='is_present',
            field=models.BooleanField(default=True),
        ),
        migrations.AlterField(
            model_name='user',
            name='user_type',
            field=models.CharField(choices=[('Admin', 'Admin'), ('District_Admin', 'District_Admin'), ('Employee', 'Employee')], default='Employee', max_length=255),
        ),
    ]

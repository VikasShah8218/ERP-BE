# Generated by Django 5.1.3 on 2024-11-29 16:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('structure', '0002_alter_zonelog_zone'),
    ]

    operations = [
        migrations.AddField(
            model_name='districtlog',
            name='structure_count',
            field=models.JSONField(blank=True, default=dict, null=True),
        ),
        migrations.AddField(
            model_name='equipmentlog',
            name='structure_count',
            field=models.JSONField(blank=True, default=dict, null=True),
        ),
        migrations.AddField(
            model_name='junctionlog',
            name='structure_count',
            field=models.JSONField(blank=True, default=dict, null=True),
        ),
        migrations.AddField(
            model_name='landmarklog',
            name='structure_count',
            field=models.JSONField(blank=True, default=dict, null=True),
        ),
        migrations.AddField(
            model_name='polelog',
            name='structure_count',
            field=models.JSONField(blank=True, default=dict, null=True),
        ),
        migrations.AddField(
            model_name='zonelog',
            name='structure_count',
            field=models.JSONField(blank=True, default=dict, null=True),
        ),
        migrations.AlterField(
            model_name='districtlog',
            name='current_values',
            field=models.JSONField(default=dict),
        ),
        migrations.AlterField(
            model_name='districtlog',
            name='previous_values',
            field=models.JSONField(default=dict),
        ),
        migrations.AlterField(
            model_name='equipmentlog',
            name='current_values',
            field=models.JSONField(default=dict),
        ),
        migrations.AlterField(
            model_name='equipmentlog',
            name='previous_values',
            field=models.JSONField(default=dict),
        ),
        migrations.AlterField(
            model_name='junctionlog',
            name='current_values',
            field=models.JSONField(default=dict),
        ),
        migrations.AlterField(
            model_name='junctionlog',
            name='previous_values',
            field=models.JSONField(default=dict),
        ),
        migrations.AlterField(
            model_name='landmarklog',
            name='current_values',
            field=models.JSONField(default=dict),
        ),
        migrations.AlterField(
            model_name='landmarklog',
            name='previous_values',
            field=models.JSONField(default=dict),
        ),
        migrations.AlterField(
            model_name='polelog',
            name='current_values',
            field=models.JSONField(default=dict),
        ),
        migrations.AlterField(
            model_name='polelog',
            name='previous_values',
            field=models.JSONField(default=dict),
        ),
        migrations.AlterField(
            model_name='zonelog',
            name='current_values',
            field=models.JSONField(default=dict),
        ),
        migrations.AlterField(
            model_name='zonelog',
            name='previous_values',
            field=models.JSONField(default=dict),
        ),
    ]

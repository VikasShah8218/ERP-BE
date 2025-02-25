# Generated by Django 5.1.3 on 2025-02-24 09:20

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0014_alter_approval_status_alter_product_status_and_more'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='DailyEntry',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('items', models.JSONField(blank=True, default=dict, null=True)),
                ('note', models.TextField(blank=True, null=True)),
                ('description', models.TextField(blank=True, null=True)),
                ('created_on', models.DateTimeField(auto_now_add=True, null=True)),
                ('updated_on', models.DateTimeField(auto_now=True)),
                ('employee', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='entry_emp', to=settings.AUTH_USER_MODEL)),
                ('location', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='entry_location', to='store.location')),
            ],
            options={
                'db_table': 'store_daily_entry',
            },
        ),
    ]

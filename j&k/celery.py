from __future__ import absolute_import, unicode_literals
import os
from celery import Celery
from celery.signals import worker_init

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'j&k.settings')
app = Celery('j&k')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.conf.worker_prefetch_multiplier = 10
app.autodiscover_tasks()


@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')

@worker_init.connect
def setup(sender=None, conf=None, **kwargs):
    # Preload heavy modules or setup database connections here
    print("Worker initialized and ready to process tasks!")
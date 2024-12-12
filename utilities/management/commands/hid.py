from apps.hid.main import *
from django.core.management.base import BaseCommand
from django.utils import timezone
import threading
import redis
import time

REDIS = redis.Redis(host='localhost', port=6379, db=0)

#  |--------------------------------------------------------------|
#  |                                                              |
#  |                        Start Thread                          |
#  |                                                              |
#  |--------------------------------------------------------------|

class Command(BaseCommand):
    help = 'Listen to All HID Devices'
    def handle(self, *args, **options):
        if write_command('11 512 512 0 0 1 0 0 0 0 0'):
            REDIS.set("stop_thread", "0")
            thread_1 = threading.Thread(target=get_message)
            thread_1.daemon = True 
            thread_1.start()
            time.sleep(0.1)
            r1,r2 = connect_to_all()
            print(r1,r2)
        else:
            print("Something went wrong")    
        thread_2 = threading.Thread(target=priodic_check_status)
        thread_2.start()   

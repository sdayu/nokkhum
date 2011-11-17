'''
Created on Nov 16, 2011

@author: boatkrap
'''
import threading
import datetime
import time

from twisted.python import log

from nokkhum import model
from nokkhum.controller.manager import camera

class CameraCommandMonitor(threading.Thread):
    def run(self):
        time_to_sleep = 30
    
        cam_manager = camera.CameraManager()
        
        while(True):
            start_time = datetime.datetime.now()
            
            camera_commands = model.CameraCommandQueue.objects(status='Starting').all()
            for camera_command in camera_commands:
                pass
            
            end_time = datetime.datetime.now()
            
            delta = start_time - end_time
            sleep_time = time_to_sleep - delta.total_seconds()
            
            if sleep_time > 0:
                time.sleep(sleep_time)

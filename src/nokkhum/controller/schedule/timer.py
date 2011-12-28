'''
Created on Dec 2, 2011

@author: boatkrap
'''


import threading
import datetime
import time

import logging
logger = logging.getLogger(__name__)

from camera import CameraScheduling
from ..monitor.camera import CameraMonitoring

class Timer(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.name = "Timer"
        self.daemon = True
        
        self.camera_sheduling = None
        self.camera_monitoring = None
        
        self.wakeup_every = 10
        
    def run(self):
        
        while(True):
            start_time = datetime.datetime.now()
            
            # check thread is alive
            if self.camera_sheduling is not None:
                if not self.camera_sheduling.is_alive():
                    self.camera_sheduling.join()
                    self.camera_sheduling = None
                    
            if self.camera_monitoring is not None:
                if not self.camera_monitoring.is_alive():
                    self.camera_monitoring.join()
                    self.camera_monitoring = None
                    
            if self.camera_sheduling is None:
                self.camera_sheduling = CameraScheduling()
                self.camera_sheduling.start()
                
            if self.camera_monitoring is None:
                self.camera_monitoring = CameraMonitoring()
                self.camera_monitoring.start()
                
                                          
            end_time = datetime.datetime.now()
            
            delta = start_time - end_time
            sleep_time =  self.wakeup_every - int(delta.total_seconds())
            
            if sleep_time > 0:
                logger.debug("Timer sleep %d "%sleep_time)
                time.sleep(sleep_time)
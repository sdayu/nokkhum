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
from ..manager.storage import Storage

class Timer(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.name = self.__class__.__name__
        self.daemon = True
        
        self.camera_sheduling = None
        self.camera_monitoring = None
        self.clear_storage = None
        
        self.wakeup_every = 10
        
        self._running = False
    
    def __start_scheduling(self):
        if self.camera_sheduling is not None:
            if not self.camera_sheduling.is_alive():
                self.camera_sheduling.join()
                self.camera_sheduling = None
                
        if self.camera_monitoring is not None:
            if not self.camera_monitoring.is_alive():
                self.camera_monitoring.join()
                self.camera_monitoring = None
                
        if self.clear_storage is not None:
            if not self.clear_storage.is_alive():
                self.clear_storage.join()
                self.clear_storage = None
                
        if self.camera_sheduling is None:
            self.camera_sheduling = CameraScheduling()
            self.camera_sheduling.start()
            
        if self.camera_monitoring is None:
            self.camera_monitoring = CameraMonitoring()
            self.camera_monitoring.start()
            
        current_time = datetime.datetime.now()
        if current_time.hour == 1 \
            and (current_time.minute >= 30 or current_time.minute < 40)\
            and self.clear_storage is None:
            self.clear_storage = Storage()
            self.clear_storage.start()
    
    def run(self):
        self._running = True
        
        while(self._running):
            start_time = datetime.datetime.now()
            
            # check thread is alive
            logger.debug("Timer Thread Weakup")
            
            try:
                self.__start_scheduling()
            except Exception as e:
                logger.exception(e)    
                
            end_time = datetime.datetime.now()
            
            delta = start_time - end_time
            sleep_time =  self.wakeup_every - int(delta.total_seconds())
            
            if sleep_time > 0:
                logger.debug("Timer sleep %d "%sleep_time)
                time.sleep(sleep_time)
        
        logger.debug("Timer Exit Loop")
        
    def stop(self):
        self._running = False
        logger.debug("Timer Thread Stop")
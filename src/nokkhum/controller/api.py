'''
Created on Jan 11, 2012

@author: boatkrap
'''

import threading
from ..messaging import connection

from nokkhum.controller.compute import update
from nokkhum.controller import schedule

import logging
logger = logging.getLogger(__name__)

class ControllerApi():
    def __init__(self):
        self._running = False
        
        self.update_status = update.UpdateStatus()
        self.timer = schedule.timer.Timer()
    
        self.rpc_client = connection.default_connection.get_rpc_factory().get_default_rpc_client()
        
        
    def start(self):
        self._running = True
        self.update_status.start()
        self.timer.start()
        while self._running:
            logger.debug("drain_event")
            connection.default_connection.drain_events()

        
    def stop(self):
        self._running = False
        
        self.update_status.stop()
        self.timer.stop()
        
        self.update_status.join()
        self.timer.join()
        
        connection.default_connection.release()
        
        
        
        
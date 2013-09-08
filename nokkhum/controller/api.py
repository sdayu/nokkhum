'''
Created on Jan 11, 2012

@author: boatkrap
'''

from ..messaging import connection

from nokkhum import config
from nokkhum.controller.compute_node import update
from nokkhum.controller import schedule
import time
import netifaces

import logging
logger = logging.getLogger(__name__)

class ControllerApi():
    
    def __init__(self):
        self._running = False
        
        self.update_status = update.UpdateStatus()
        self.timer = schedule.timer.Timer()
        
        
        ip = "127.0.0.1"
        try:
            ip = netifaces.ifaddresses(config.Configurator.settings.get('nokkhum.controller.interface')).setdefault(netifaces.AF_INET)[0]['addr']
        except Exception as e:
            logger.exception(e)
            ip = netifaces.ifaddresses('lo').setdefault(netifaces.AF_INET)[0]['addr']
    
        self.rpc_client = connection.default_connection.get_rpc_factory().get_default_rpc_client(ip)
        
        
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
        
        
        
        
'''
Created on Jan 11, 2012

@author: boatkrap
'''

import threading
from ..common.messages import connection

from nokkhum.controller.compute import update

import logging
logger = logging.getLogger(__name__)

class ControllerApi(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self._running = False
        self.update_status = update.UpdateStatus()
        self.rpc_client = connection.default_connection.get_rpc_factory().get_default_rpc_client()
        
        
    def run(self):
        self._running = True
        logger.debug("api drain0")
        self.update_status.start()
        logger.debug("api drain")
        connection.default_connection.drain_events()
        logger.debug("end api drain")

        
    def stop(self):
        self._running = False
        self.update_status.stop()
        connection.default_connection.release()
'''
Created on Aug 23, 2012

@author: boatkrap
'''
from ..manager.compute_node import ComputeNodeManager
from ..manager.vm import VMManager

import threading
import logging
logger = logging.getLogger(__name__)


class VMMonitoring(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.name = "VM Monitoring"
        self.daemon = True
        self.compute_node_manager = ComputeNodeManager()
    
    def run(self):
        logger.debug("VM Monitoring working")
        self.__monitor_VM()
        logger.debug("VM Monitoring working")

            
    def __monitor_VM(self):
        ''''''
        if self.compute_node_manager.get_compute_node_avialable_resource() is not None:
            return
        
        self.vm_manager = VMManager()
        logger.debug("VM --> get vm")
        self.vm_manager.acquire()
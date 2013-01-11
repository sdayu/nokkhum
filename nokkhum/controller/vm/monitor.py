'''
Created on Aug 23, 2012

@author: boatkrap
'''
from ..compute_node.manager import ComputeNodeManager
from .manager import VMManager

import threading
import logging
import datetime
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
        logger.debug("VM Monitoring finish")

            
    def __monitor_VM(self):
        ''''''
        if self.compute_node_manager.get_compute_node_avialable_resource() is not None:
            return
        
        
        self.vm_manager = VMManager()
        compute_nodes = self.vm_manager.list_vm_compute_node()
        
        for compute_node in compute_nodes:
            if datetime.datetime.now() - compute_node.vm.start_instance_date < datetime.timedelta(minutes=10):
                logger.debug("VM --> in wait list")
                return 
        
        logger.debug("VM --> get vm")
        self.vm_manager.acquire()
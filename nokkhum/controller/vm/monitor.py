'''
Created on Aug 23, 2012

@author: boatkrap
'''
from ..compute_node.manager import ComputeNodeManager
from .manager import VMManager
from nokkhum import models

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
        self.__monitor()
        self.__terminate()
        logger.debug("VM Monitoring finish")
        
    def __terminate(self):
        logger.debug("VM Monitoring check for terminate")
        compute_nodes = models.ComputeNode.objects().all()
            
    def __monitor(self):
        ''''''
        logger.debug("VM Monitoring check for acquisition")
        processor_command = models.ProcessorCommand.objects(action__iexact="start", status__iexact='waiting').first()
        
        if models.ProcessorCommandQueue.objects(processor_command=processor_command).first() is None:
            return
        
        if self.compute_node_manager.get_compute_node_available_resource() is not None:
            return
        
        logger.debug("VM There are no available resource")
        self.vm_manager = VMManager()
        compute_nodes = self.vm_manager.list_vm_compute_node()
        
        for compute_node in compute_nodes:
            if datetime.datetime.now() - compute_node.vm.start_instance_date < datetime.timedelta(minutes=20):
                if compute_node.vm.status == 'pending':
                    logger.debug("VM --> in wait list")
                    return 
        
        logger.debug("VM --> get vm")
        self.vm_manager.acquire()
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
    
        self.vm_manager = VMManager()
        
    def run(self):
        logger.debug("VM Monitoring working")
        self.__monitor()
        logger.debug("VM Monitoring finish")
        
    def __manage(self):
#         logger.debug("VM Monitoring check for terminate or reboot")
#         compute_nodes = models.ComputeNode.objects(vm__ne=None, vm__status__ne='terminate').all()
#         for compute_node in compute_nodes:
#             if compute_node.is_online():
#                 if compute_node.cpu.used < 5:
#                     logger.debug("VM Monitoring terminate compute node id %s instance id %s"%(compute_node.id, compute_node.vm.instance_id))
#                     self.vm_manager.terminate(compute_node.vm.instance_id)
#                     compute_node.vm.terminated_date = datetime.datetime.now()
#                     compute_node.save()
#             else:
#                 logger.debug("VM Monitoring reboot compute node id %s instance id %s"%(compute_node.id, compute_node.vm.instance_id))
#                 ec2_instance = self.vm_manager.find_instance(compute_node.vm.instance_id)
#                 if ec2_instance:
#                     self.vm_manager.reboot(compute_node.vm.instance_id)
#                 else:
#                     logger.debug("VM Monitoring compute node id %s instance id %s already terminated"%(compute_node.id, compute_node.vm.instance_id))
#                     compute_node.vm.status = 'terminate'
#                     compute_node.vm.terminated_date = datetime.datetime.now()
#                     compute_node.save()
                    
    
    def __acquire(self):
        logger.debug("VM Monitoring check for acquisition")
        processor_command = models.ProcessorCommand.objects(action__iexact="start", status__iexact='waiting').first()
        
        if models.ProcessorCommandQueue.objects(processor_command=processor_command).first() is None:
            return
        
        if self.compute_node_manager.get_compute_node_available_resource() is not None:
            return
        
        logger.debug("VM There are no available resource")
        compute_nodes = self.vm_manager.list_vm_compute_node()
        
        for compute_node in compute_nodes:
            if datetime.datetime.now() - compute_node.vm.started_instance_date < datetime.timedelta(minutes=20):
                if compute_node.vm.status == 'pending':
                    logger.debug("VM --> in wait list")
                    return 
        
        logger.debug("VM --> get vm")
        self.vm_manager.acquire()
    
    def __monitor(self):
        ''''''
        self.__manage()
        self.__acquire()
        
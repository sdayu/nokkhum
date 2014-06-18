'''
Created on Aug 23, 2012

@author: boatkrap
'''
from ..compute_node.manager import ComputeNodeManager
from .manager import VMManager
from nokkhum import models

from nokkhum.controller.compute_node.resource_predictor import KalmanPredictor

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
        ''''''
        logger.debug("VM Monitoring check for terminate or reboot")
        compute_nodes = self.vm_manager.list_vm_compute_node()
        for compute_node in compute_nodes:
            if compute_node.is_online():
                
                if datetime.datetime.now() - compute_node.vm.started_instance_date < datetime.timedelta(minutes=30):
                    logger.debug('VM Monitoring compute node id %s instance id %s begin started' % (compute_node.id, compute_node.vm.instance_id))
                    continue
                
                if compute_node.cpu.used > 5:
                    logger.debug('VM Monitoring compute node id %s instance id %s got CPU usage more than 5%%' % (compute_node.id, compute_node.vm.instance_id))
                    continue
                
                logger.debug("VM Monitoring check compute node id %s instance id %s"%(compute_node.id, compute_node.vm.instance_id))
                records = models.ComputeNodeReport.objects(compute_node=compute_node, 
                                                       reported_date__gt=datetime.datetime.now() - datetime.timedelta(minutes=2))\
                                                        .order_by("-reported_date").limit(20)
                
                has_processor = False
                for record in records:
                    if len(record.processor_status) > 0:
                        has_processor = True
                        logger.debug("VM Monitoring predict compute node id %s instance id %s has processors"%(compute_node.id, compute_node.vm.instance_id))
                        break
                
                if has_processor:
                    continue
                
                cpu = [record.cpu.used for record in records]
                cpu.reverse()
                kp = KalmanPredictor()
                cpu_predict = kp.predict(cpu)
                
                if cpu_predict < 5:
                    logger.debug("VM Monitoring terminate compute node id %s instance id %s"%(compute_node.id, compute_node.vm.instance_id))
                    self.vm_manager.terminate(compute_node.vm.instance_id)
            else:
                logger.debug("VM Monitoring check for reboot compute node id %s instance id %s"%(compute_node.id, compute_node.vm.instance_id))
                ec2_instance = self.vm_manager.get(compute_node.vm.instance_id)
                if ec2_instance:
                    if 'responsed_date' in compute_node.extra:
                        logger.debug("VM Monitoring reboot compute node id %s instance id %s"%(compute_node.id, compute_node.vm.instance_id))
                        self.vm_manager.reboot(compute_node.vm.instance_id)
                else:
                    logger.debug("VM Monitoring compute node id %s instance id %s already terminated"%(compute_node.id, compute_node.vm.instance_id))
                    compute_node.status = 'terminate'
                    compute_node.vm.status = 'terminate'
                    compute_node.updated_date = datetime.datetime.now()
                    compute_node.save()
                    
    
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
                    logger.debug("VM compute node id: %s instance id: %s in wait list"%(compute_node.id, compute_node.vm.instance_id))
                    return 
                elif 'responsed_date' not in compute_node.extra:
                    logger.debug("VM compute node id: %s instance id: %s in wait for first time response"%(compute_node.id, compute_node.vm.instance_id))
                    return
                elif 'responsed_date' in compute_node.extra:
                    if compute_node.extra['responsed_date'][-1] > (datetime.datetime.now() - datetime.timedelta(seconds=10)):
                        logger.debug("VM compute node id: %s instance id: %s in wait for stable report resource"%(compute_node.id, compute_node.vm.instance_id))
                        return
        
        logger.debug("VM --> get vm")
        self.vm_manager.acquire()
    
    def __monitor(self):
        ''''''
        self.__manage()
        self.__acquire()
        
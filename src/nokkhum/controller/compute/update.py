'''
Created on Dec 23, 2011

@author: boatkrap
'''

import threading, datetime

from nokkhum.common.messages import consumer
import logging

from nokkhum.common import models

logger = logging.getLogger(__name__)

class ComputeNodeResource:

    def update_system_infomation(self, args):
        try:
            name        = args['name']
            cpu_count   = args['cpu_count']
            total_ram   = args['total_ram']
            system      = args['system']
            machine     = args['machine']
            host        = args['ip']
            
            compute_node = models.ComputeNode.objects(name=name, host=host).first()
            if compute_node is None:
                compute_node = models.ComputeNode()
                compute_node.name = name
                compute_node.host = host
                
            cpu = models.CPUInfomation()
            cpu.count = cpu_count
            
            memory = models.MemoryInfomation()
            memory.total = total_ram
            
            compute_node.machine = machine
            compute_node.system  = system
            compute_node.cpu     = cpu
            compute_node.memory  = memory
            compute_node.update_date = datetime.datetime.now()
            compute_node.save()
        
            logger.debug( 'Compute node name: "%s" update system info complete' % ( name ) )
        except Exception as e:
            logger.exception(e)

        

    def update_resource(self, args):
        try:
            name        = args['name']
            cpu         = args['cpu']
            memory      = args['memory']
            cameras     = args['cameras']
            host        = args['ip']
            
            compute_node = models.ComputeNode.objects(name=name, host=host).first()
            if compute_node is None:
                logger.debug("compute node: %s unavailable" % name)
                return 
            
            compute_node.cpu.usage   = cpu["usage"]
            compute_node.cpu.usage_per_cpu = cpu["percpu"]
            
            compute_node.memory.total = memory["total"]
            compute_node.memory.used  = memory["used"]
            compute_node.memory.free  = memory["free"]
            
            current_time = datetime.datetime.now()
            compute_node.update_date = current_time
            compute_node.save()

            for id in cameras:
                camera = models.Camera.objects().get(id=id)
                camera.operating.status = "Running"
                camera.operating.update_date = current_time
                camera.operating.compute_node = compute_node
                camera.save()
                
            logger.debug( 'Compute node name: "%s" update resource complete' % ( name ) )
        except Exception as e:
            logger.exception(e)


class UpdateStatus(threading.Thread):
    
    def __init__(self):
        threading.Thread.__init__(self)
        self._consumer = consumer.ConsumerFactory().get_consumer("nokkhum_compute.update_status")
        self.connection = consumer.ConsumerFactory().get_connection()
        self.update()
        self.daemon = True
        self._running = False
        self._cn_resource = ComputeNodeResource()
        
    def update(self):
        def process_msg(body, message):
            cn_resource = ComputeNodeResource()
            if body["action"] == "update_system_infomation":
                cn_resource.update_system_infomation(body["args"])
            elif body["action"] == "update_resource":
                cn_resource.update_resource(body["args"])
            message.ack()
        
        self._consumer.register(process_msg)

        
    def run(self):

        self._running = True
        while self._running:
            self.connection.drain_events()
            
    def stop(self):
        self._running = False

    
    
    
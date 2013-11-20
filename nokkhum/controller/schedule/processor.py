'''
Created on Nov 23, 2011

@author: boatkrap
'''

import threading
import datetime
import time

from nokkhum import models
from nokkhum.controller.processor import manager

import logging
logger = logging.getLogger(__name__)

class ProcessorCommandProcessing:
    def __init__(self):
        self.processor_manager = manager.ProcessorManager()
        
    def start(self, command, compute_node):

        command.status = "processing"
        command.update_date = datetime.datetime.now()
        command.save()
        
        logger.debug("Starting processor id %s to host %s IP %s"%(command.processor.id, compute_node.name, compute_node.host))
        
        response = None
        
        processor = command.processor
        try:
            if processor.operating.status == "running":
                raise Exception('processor id %s already running'%str(processor.id))
            
            processor.operating.user_command = "run"
            processor.operating.status = "starting"
            processor.operating.update_date = datetime.datetime.now()
            processor.save()
            
            response = self.processor_manager.start_processor(compute_node, command.processor)
            if response['success']:
                command.status = "complete"
                processor.operating.status = "running"
                processor.operating.compute_node = compute_node
                processor.operating.update_date = datetime.datetime.now()
            else:
                raise Exception('start processor fail')
        except Exception as e:
            logger.exception(e)
#            command.camera.operating.status = "Stop"
#            command.camera.operating.update_date = datetime.datetime.now()
            command.message = str(e)
            command.status = "error"
            command.update_date = datetime.datetime.now()
        
        processor.save()
        command.save()
        
        msg = ''
        if command.message is not None:
            msg = command.message + '\n'
            
        if response:
            msg += response["comment"]
        
        command.message = msg
        command.save()
        
        self.end_process(command)

    def stop(self, command):
        
        command.status = "processing"
        command.update_date = datetime.datetime.now()
        command.save()
        
        compute_node = command.processor.operating.compute_node
        
        if compute_node:
            logger.debug("Stopping processor id %s to host %s ip %s"%(command.processor.id, compute_node.name, compute_node.host))
        
        response = None
        command.processor.operating.user_command = "stop"
        command.processor.operating.status = "stopping"
        command.processor.operating.update_date = datetime.datetime.now()
        command.processor.save()
            
        try:
            if not compute_node:
                raise Exception('No available compute node')
            
            if not compute_node.is_online():
                raise Exception('Compute node offline')
            
            processor = command.processor
            if datetime.datetime.now() - processor.operating.update_date < datetime.timedelta(seconds=30):
                response = self.processor_manager.stop_processor(compute_node, command.processor)
                
            command.processor.operating.status = "stop"
            command.processor.operating.update_date = datetime.datetime.now()
            command.processor.operating.compute_node = compute_node
            command.status = "complete"
        except Exception as e:
            logger.exception(e)
            command.processor.operating.status = "stop"
            command.processor.operating.update_date = datetime.datetime.now()
            command.status = "error"
            command.update_date = datetime.datetime.now()
        
        command.processor.save()
        command.save()
        
        msg = ''
        if command.message is not None:
            msg = command.message
        
        if response:    
            msg += response["comment"]
        
        command.message = msg
        command.save()
        self.end_process(command)
    
    def end_process(self, command):

        command.attributes = manager.ProcessorAttributesBuilder(command.processor).get_attribute()
        command.compute_node = command.processor.operating.compute_node
        command.complete_date = datetime.datetime.now()
        
        command.save()
        
        this_queue = models.ProcessorCommandQueue.objects(processor_command=command).first()
        if this_queue:
            this_queue.delete()
        

class ProcessorScheduling(threading.Thread):
    def __init__(self):
        ''''''
        from .. import compute_node
        
        threading.Thread.__init__(self)
        self.compute_node_manager = compute_node.manager.ComputeNodeManager()
        self.name = "Processor Scheduling"
        self.daemon = True
        
    def __remove_command_unavailable(self):
        
        # check processing status expired
        queue = models.ProcessorCommandQueue.objects().all()        
        
        for command in queue:
            processor_command = command.processor_command
            if processor_command.status in ["processing", "error"]:
                td  = datetime.datetime.now() - datetime.timedelta(minutes=2)
                if processor_command.update_date > td:
                    continue
            else:
                continue
            try:
                current_date =  datetime.datetime.now()
                extra = dict(
                            last_status = processor_command.status,
                            last_update_date = processor_command.update_date,
                            detectable_date = current_date,
                            
                        )

                processor_command.extra.update(extra)
                processor_command.message = processor_command.message+"\n\nextra: %s"%extra
                processor_command.save()
                
                this_queue = models.ProcessorCommandQueue.objects(processor_command = processor_command).first()
                if this_queue:
                    this_queue.delete()
                
            except Exception as e:
                logger.exception(e)
        
    def run(self):
        
        logger.debug(self.name+": working")
        self.__remove_command_unavailable()
        
        logger.debug(self.name+" get %d command" % models.ProcessorCommandQueue.objects().count())
        
        def get_command():
            for this_queue in models.ProcessorCommandQueue.objects().order_by('+id').all():
                if this_queue.processor_command.status == 'waiting':
                    return this_queue
                
            return None

        # for this_queue in models.ProcessorCommandQueue.objects().order_by('+id').all():
        while get_command() is not None:
            this_queue = get_command()    
            
            if this_queue.processor_command.status != 'waiting':
                logger.debug("status not waiting:"+ this_queue.processor_command.status)
                continue
            
            if self.compute_node_manager.get_available_compute_node().count() == 0:
                logger.debug("There are no available compute node")
                break
            
            # this_queue = models.ProcessorCommandQueue.objects(processor_command__status = "waiting").order_by('+id').first()
            
            this_queue.processor_command.process_date = datetime.datetime.now()
            if 'process_count' not in this_queue.processor_command.extra:
                this_queue.processor_command.extra['process_count'] = 0

            this_queue.processor_command.extra['process_count'] += 1
            this_queue.save()
            
            compute_node = None
            if this_queue.processor_command.action == "start"\
                or this_queue.processor_command.action == "restart":
                
                compute_node = self.compute_node_manager.get_compute_node_available_resource()
                if compute_node is None:
                    logger.debug("There are no available resource")
                    break
                else:
                    logger.debug("Compute node ip: %s cpu %s ram %s "
                             % (compute_node.host, 
                                compute_node.cpu.used, 
                                compute_node.memory.free)
                             )                
                
            try:
                ccp = ProcessorCommandProcessing()
                if this_queue.processor_command.action == "start":
                    ccp.start(this_queue.processor_command, compute_node)
                elif this_queue.processor_command.action == "stop":
                    ccp.stop(this_queue.processor_command)
                elif this_queue.processor_command.action == "restart":
                    ccp.stop(this_queue.processor_command)
                    ccp.start(this_queue, compute_node)
            except Exception as e:
                logger.exception(e)

        logger.debug(self.name+": terminate")
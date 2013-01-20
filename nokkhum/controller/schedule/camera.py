'''
Created on Nov 23, 2011

@author: boatkrap
'''

import threading
import datetime
import time

from nokkhum import models
from nokkhum.controller.camera import manager
from .. import compute_node

import logging
logger = logging.getLogger(__name__)

class CameraCommandProcessing:
    def __init__(self):
        self.camera_manager = manager.CameraManager()
        
    def start(self, command, compute_node):
    
        command.status = "processing"
        command.update_date = datetime.datetime.now()
        command.save()
        
        logger.debug("Starting camera id %d to %s ip %s"%(command.camera.id, compute_node.name, compute_node.host))
        
        response = None
        command.camera.operating.status = "starting"
        command.camera.operating.update_date = datetime.datetime.now()
        command.camera.save()
            
        try:
            response = self.camera_manager.start_camera(compute_node, command.camera)
            if response['success']:
                command.status = "complete"
                command.camera.operating.status = "running"
                command.camera.operating.compute_node = compute_node
                command.camera.operating.update_date = datetime.datetime.now()
            else:
                raise Exception('start camera fail')
        except Exception as e:
            logger.exception(e)
#            command.camera.operating.status = "Stop"
#            command.camera.operating.update_date = datetime.datetime.now()
            command.message = str(e)
            command.status = "error"
            command.update_date = datetime.datetime.now()
        
        command.camera.save()
        command.save()
        
        msg = ''
        if command.message is not None:
            msg = command.message + '\n'
            
        if response:
            msg += response["comment"]
        
        cmd_log         = models.CommandLog()
        cmd_log.action  = command.action
        cmd_log.attributes = manager.CameraAttributesBuilder(command.camera).get_attribute()
        cmd_log.compute_node = compute_node
        cmd_log.camera = command.camera
        cmd_log.command_date = command.command_date
        cmd_log.complete_date = datetime.datetime.now()
        cmd_log.owner = command.owner
        cmd_log.message = msg
        cmd_log.status = command.status
        cmd_log.save()
        
        command.delete()
        
    def stop(self, command):
    
        command.status = "processing"
        command.update_date = datetime.datetime.now()
        command.save()
        
        compute_node = command.camera.operating.compute_node
        
        if compute_node:
            logger.debug("Stopping camera id %d to %s ip %s"%(command.camera.id, compute_node.name, compute_node.host))
        
        response = None
        command.camera.operating.status = "stopping"
        command.camera.operating.update_date = datetime.datetime.now()
        command.camera.save()
            
        try:
            if not compute_node:
                raise Exception('No available compute node')
            response = self.camera_manager.stop_camera(compute_node, command.camera)
            command.camera.operating.status = "stop"
            command.camera.operating.update_date = datetime.datetime.now()
            command.camera.operating.compute_node = compute_node
            command.status = "complete"
        except:
            command.camera.operating.status = "stop"
            command.camera.operating.update_date = datetime.datetime.now()
            command.status = "error"
            command.update_date = datetime.datetime.now()
        
        command.camera.save()
        command.save()
        
        msg = ''
        if command.message is not None:
            msg = command.message
        
        if response:    
            msg += response["comment"]
        
        cmd_log         = models.CommandLog()
        cmd_log.action  = command.action
        cmd_log.attributes = manager.CameraAttributesBuilder(command.camera).get_attribute()
        cmd_log.compute_node = compute_node
        cmd_log.camera = command.camera
        cmd_log.command_date = command.command_date
        cmd_log.complete_date = datetime.datetime.now()
        cmd_log.owner = command.owner
        cmd_log.message = msg
        cmd_log.status = command.status
        cmd_log.save()
        
        command.delete()
        

class CameraScheduling(threading.Thread):
    def __init__(self):
        ''''''
        threading.Thread.__init__(self)
        self.compute_node_manager = compute_node.manager.ComputeNodeManager()
        self.name = "Camera Scheduling"
        self.daemon = True
        
    def run(self):
        
        logger.debug(self.name+": working")
        td  = datetime.datetime.now() - datetime.timedelta(minutes=2)
        
        # check processing status expired
                
        while models.CameraCommandQueue.objects(status="processing", update_date__lt=td).count() > 0:
            try:
                command = models.CameraCommandQueue.objects(status="processing").order_by('+id').first()
                command.delete()
                
            except Exception as e:
                logger.exception(e)
        
        while models.CameraCommandQueue.objects(status = "waiting").count() > 0:
            
            if len(self.compute_node_manager.get_available_compute_node()) == 0:
                break
            
            command = models.CameraCommandQueue.objects(status = "waiting").order_by('+id').first()
            
            compute_node = None
            if command.action == "start":    
                compute_node = self.compute_node_manager.get_compute_node_available_resource()
                if compute_node is None:
                    logger.debug("There are no available resource")
                    
                    command = models.CameraCommandQueue.objects(status = "waiting", action__ne="start").order_by('+id').first()
                    
                    if command is None:
                        break
                
            try:
                if command.action == "start":
                    ccp = CameraCommandProcessing()
                    ccp.start(command, compute_node)
                elif command.action == "stop":
                    ccp = CameraCommandProcessing()
                    ccp.stop(command)
            except Exception as e:
                logger.exception(e)

        logger.debug(self.name+": terminate")
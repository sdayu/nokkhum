'''
Created on Nov 23, 2011

@author: boatkrap
'''

import threading
import datetime
import time

from nokkhum import model
from nokkhum.controller import manager

from twisted.python import log

class CameraCommandProcessing:
    def __init__(self):
        self.camera_manager = manager.camera.CameraManager()
        
    def start(self, command, compute_node):
    
        command.status = "Processing"
        command.update_date = datetime.datetime.now()
        command.save()
        
        log.msg("Starting camera id %d to %s ip %s"%(command.camera.id, compute_node.name, compute_node.host) )
        
        result = None
        try:
            command.camera.operating.status = "Starting"
            command.camera.operating.update_date = datetime.datetime.now()
            command.camera.save()
            
            result = self.camera_manager.start_camera(compute_node, command.camera)
        except:
            log.err()
            command.camera.operating.status = "Stop"
            command.camera.operating.update_date = datetime.datetime.now()
            
            command.status = "Error"
            command.update_date = datetime.datetime.now()
            command.save()
            return False
        
        command.camera.operating.status = "Running"
        command.camera.operating.update_date = datetime.datetime.now()
        command.camera.operating.compute_node = compute_node
        command.status = "Complete"
        command.camera.save()
        
        msg = ''
        if command.message is not None:
            msg = command.message
            
        msg += result["result"]
        
        cmd_log         = model.CommandLog()
        cmd_log.action  = command.action
        cmd_log.attributes = manager.camera.CameraAttributesBuilder(command.camera).get_attribute()
        cmd_log.compute_node = compute_node
        cmd_log.camera = command.camera
        cmd_log.command_date = command.command_date
        cmd_log.complete_date = datetime.datetime.now()
        cmd_log.owner = command.owner
        cmd_log.message = msg
        cmd_log.save()
        
        command.delete()
        
    def stop(self, command):
    
        command.status = "Processing"
        command.update_date = datetime.datetime.now()
        command.save()
        
        compute_node = command.camera.operating.compute_node
        
        log.msg("Stopping camera id %d to %s ip %s"%(command.camera.id, compute_node.name, compute_node.host) )
        result = None
        try:
            command.camera.operating.status = "Stopping"
            command.camera.operating.update_date = datetime.datetime.now()
            command.camera.save()
            
            result = self.camera_manager.stop_camera(compute_node, command.camera)
        except:
            log.err()
            command.camera.operating.status = "Stop"
            command.camera.operating.update_date = datetime.datetime.now()
            
            command.status = "Error"
            command.update_date = datetime.datetime.now()
            command.save()
            return False
        
        command.camera.operating.status = "Stop"
        command.camera.operating.update_date = datetime.datetime.now()
        command.camera.operating.compute_node = compute_node
        command.status = "Complete"
        command.camera.save()
        
        msg = ''
        if command.message is not None:
            msg = command.message
            
        msg += result["result"]
        
        cmd_log         = model.CommandLog()
        cmd_log.action  = command.action
        cmd_log.attributes = manager.camera.CameraAttributesBuilder(command.camera).get_attribute()
        cmd_log.compute_node = compute_node
        cmd_log.camera = command.camera
        cmd_log.command_date = command.command_date
        cmd_log.complete_date = datetime.datetime.now()
        cmd_log.owner = command.owner
        cmd_log.message = msg
        cmd_log.save()
        
        command.delete()
        

class CameraScheduling(threading.Thread):
    def __init__(self):
        ''''''
        threading.Thread.__init__(self)
        self.compute_node_manager = manager.compute_node.ComputeNodeManager()
        self.name = "Camera Scheduling"
        self.daemon = True
        
    def run(self):
        
        log.msg(self.name+" working")
        while model.CameraCommandQueue.objects(status = "Waiting").count() > 0:
            compute_node = self.compute_node_manager.get_compute_node_avialable_resource()
            if compute_node is None:
                log.err("There are no avialable resource")
                break
            
            command = model.CameraCommandQueue.objects(status = "Waiting").order_by('-id').first()
            if command.action == "Start":
                ccp = CameraCommandProcessing()
                ccp.start(command, compute_node)
            elif command.action == "Stop":
                ccp = CameraCommandProcessing()
                ccp.stop(command)

        log.msg(self.name+" terminate")
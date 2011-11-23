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

class CameraScheduling(threading.Thread):
    def __init__(self):
        ''''''
        threading.Thread.__init__(self)
        self.camera_manager = manager.camera.CameraManager()
        self.compute_node_manager = manager.compute_node.ComputeNodeManager()
        
    def run(self):
        time_to_sleep = 30
    
        while(True):
            start_time = datetime.datetime.now()
            
            while model.CameraCommandQueue.objects(status = "Waiting").count() > 0:
                compute_node = self.compute_node_manager.get_compute_node_avialable_resource()
                if compute_node is None:
                    log.err("There are no avialable resource")
                    break
                
                command = model.CameraCommandQueue.objects(status = "Waiting").order_by('-id').first()
                command.status = "Processing"
                command.update_date = datetime.datetime.now()
                command.save()
                
                command.camera.operating.status = "Starting"
                command.camera.operating.update_date = datetime.datetime.now()
                command.camera.save()
                
                log.msg("Starting camera to %s ip %s"%(compute_node.name, compute_node.host) )
                
                try:
                    self.camera_manager.startCamea(compute_node, command.camera)
                except:
                    log.err()
                    command.camera.operating.status = "Stop"
                    command.camera.operation.update_date = datetime.datetime.now()
                    command.status = "Error"
                    command.update_date = datetime.datetime.now()
                    command.save()
                    continue
                
                command.camera.operating.status = "Running"
                command.camera.operation.update_date = datetime.datetime.now()
                command.camera.save()
                
                cmd_log = model.CommandLog()
                cmd_log.id = command.id
                cmd_log.action = command.action
                cmd_log.attributes = ""
                cmd_log.compute_node = command.compute_node
                cmd_log.command_date = command.command_date
                cmd_log.complete_date = datetime.datetime.now()
                cmd_log.owner = command.owner
                cmd_log.save()
                
                command.delete()
                                          
            end_time = datetime.datetime.now()
            
            delta = start_time - end_time
            sleep_time = time_to_sleep - delta.total_seconds()
            
            if sleep_time > 0:
                log.msg("Camera scheduling sleep %d "%sleep_time)
                time.sleep(sleep_time)

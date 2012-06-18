'''
Created on Dec 1, 2011

@author: boatkrap
'''

import threading
import datetime

import logging
logger = logging.getLogger(__name__)

from nokkhum import models

class CameraMonitoring(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.name = "Camera Monitoring"
        self.daemon = True
        self.maximum_wait_time = 60 # in second
        
    def run(self):
        
        
        logger.debug("Camera Monitoring working")
        self.__monitor_camera_active()
        logger.debug("Camera Monitoring terminate")
        
    def __monitor_camera_active(self):
        cameras = models.Camera.objects(status='Active').all()
        current_time = datetime.datetime.now()
        for camera in cameras:
            if camera.operating.user_command == "Run":
                if camera.operating.status == "Running" or camera.operating.status == "Starting" or camera.operating.status == "Stopping":
                    diff_time = current_time - camera.operating.update_date
                    # logger.debug( "camera id: %d diff: %d s" % (camera.id, diff_time.total_seconds()))
                    if diff_time > datetime.timedelta(seconds=self.maximum_wait_time):
                        logger.debug( "camera id: %d disconnect diff: %d s" % (camera.id, diff_time.total_seconds()))
                        new_command = models.CameraCommandQueue.objects(camera=camera, action="Start").first()
                        
                        if new_command is not None:
                            continue
                        
                        new_command = models.CameraCommandQueue()
                        if camera.operating.status == "Running" or camera.operating.status == "Starting":
                            new_command.action = "Start"
                        elif camera.operating.status == "Stopping":
                            new_command.action = "Stop"
                        new_command.camera = camera
                        new_command.message = "Camera-processor disconnect.\n Restart camera by CameraMonotoring: %s" % datetime.datetime.now()
                        new_command.owner = camera.owner
                        new_command.save()
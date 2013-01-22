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
        
    def __request_new_camera_commend(self, camera, action, message):
        camera_command = models.CameraCommandQueue.objects(camera=camera, action=action).first()

        if camera_command is not None:
            return
      
        new_command = models.CameraCommandQueue()
        if camera.operating.status == "running" or camera.operating.status == "starting" \
                or camera.operating.status == "fail":
            new_command.action = "start"
        elif camera.operating.status == "stopping":
            new_command.action = "stop"
        new_command.camera = camera
        new_command.message = message
        new_command.owner = camera.owner
        new_command.command_date = datetime.datetime.now()
        new_command.update_date = datetime.datetime.now()
        new_command.save()
        
    def __monitor_camera_active(self):
        cameras = models.Camera.objects(status='active').all()
        current_time = datetime.datetime.now()
        for camera in cameras:
            if camera.operating.user_command == "run":
                if camera.operating.status == "running" or camera.operating.status == "starting":
                    diff_time = current_time - camera.operating.update_date
                    # logger.debug( "camera id: %d diff: %d s" % (camera.id, diff_time.total_seconds()))
                    if diff_time > datetime.timedelta(seconds=self.maximum_wait_time):
                        logger.debug( "camera id: %d disconnect diff: %d s" % (camera.id, diff_time.total_seconds()))
                        message = "Camera-processor disconnect.\n Restart camera by CameraMonotoring: %s" % datetime.datetime.now()
                        self.__request_new_camera_commend(camera, "start", message)
                elif camera.operating.status == "fail":
                    logger.debug( "camera id: %d status fail"%camera.id)
                    message = "Camera-processor fail.\n Restart camera by CameraMonotoring: %s" % datetime.datetime.now()
                    self.__request_new_camera_commend(camera, "start", message)
                    
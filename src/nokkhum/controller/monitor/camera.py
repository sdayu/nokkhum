'''
Created on Dec 1, 2011

@author: boatkrap
'''

import threading
import datetime
from twisted.python import log

from nokkhum.common import models

class CameraMonitoring(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.name = "Camera Monitoring"
        self.daemon = True
        self.maximum_wait_time = 90 # in second
        
    def run(self):
        cameras = models.Camera.objects(status='Active').all()
        
        log.msg("working", system=self.__class__.__name__)
        current_time = datetime.datetime.now()
        for camera in cameras:
            if camera.operating.user_command == "Run":
                if camera.operating.status == "Running":
                    diff_time = current_time - camera.operating.update_date
                    log.msg( "camera id: %d diff: %d s" % (camera.id, diff_time.total_seconds()), system=self.__class__.__name__)
                    if diff_time > datetime.timedelta(seconds=self.maximum_wait_time):
                        log.msg( "camera id: %d disconnect diff: %d s" % (camera.id, diff_time.total_seconds()), system=self.__class__.__name__)
                        new_command = models.CameraCommandQueue.objects(camera=camera, action="Start").first()
                        
                        if new_command is not None:
                            continue
                        
                        new_command = models.CameraCommandQueue()
                        new_command.action = "Start"
                        new_command.camera = camera
                        new_command.message = "restart camera by CameraMonotoring: %s" % datetime.datetime.now()
                        new_command.owner = camera.owner
                        new_command.save()
                        new_command.message = "Camera-processor disconnect"
                        
        log.msg("terminate", system=self.__class__.__name__)
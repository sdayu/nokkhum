'''
Created on Dec 1, 2011

@author: boatkrap
'''

import threading
import datetime
from twisted.python import log

from nokkhum import model

class CameraMonitoring(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.name = "Camera Monitoring"
        self.daemon = True
        self.maximum_wait_time = 2 # in minutes
        
    def run(self):
        cameras = model.Camera.objects(status='Active').all()
        
        log.msg(self.name+" working")
        current_time = datetime.datetime.now()
        for camera in cameras:
            if camera.operating.user_command == "Run":
                if camera.operating.status == "Running":
                    diff_time = current_time - camera.operating.update_date
                    print "id: ", camera.id," diff: ",diff_time.total_seconds()," s"
                    if diff_time > datetime.timedelta(minutes=self.maximum_wait_time):
                        print "-> id: ", camera.id," diff: ", diff_time.total_seconds()," s"
                        new_command = model.CameraCommandQueue.objects(camera=camera, action="Start").first()
                        
                        if new_command is not None:
                            continue
                        
                        new_command = model.CameraCommandQueue()
                        new_command.action = "Start"
                        new_command.camera = camera
                        new_command.message = "restart camera by CameraMonotoring: %s" % datetime.datetime.now()
                        new_command.owner = camera.owner
                        new_command.save()
                        
        log.msg(self.name+" terminate")
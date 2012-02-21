'''
Created on Feb 20, 2012

@author: boatkrap
'''

import threading
from nokkhum.common.storage import s3
from nokkhum.common import models
from nokkhum import controller
import datetime

import logging
logger = logging.getLogger(__name__)

class Storage(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        setting = controller.config

        access_key_id = setting.get('controller', 'nokkhum.s3.access_key_id')
        secret_access_key = setting.get('controller', 'nokkhum.s3.secret_access_key')
        host = setting.get('controller', 'nokkhum.s3.host') 
        port = setting.getint('controller', 'nokkhum.s3.port')
        secure = setting.getboolean('controller', 'nokkhum.s3.secure_connection')
        self.s3_storage = s3.S3Storage(access_key_id, secret_access_key, host, port, secure)
        
        self.daemon = True
        self.name = "S3_clear_storage_thread"
        
        logger.debug("start " + self.name)
        
    def run(self):
        buckets = self.s3_storage.get_all_buckets()
        
        for bucket in buckets:
            #print "bucket: ", bucket.name
            self.s3_storage.set_buckket_name(bucket.name)
            camera_list = self.s3_storage.list_file()
            for camera_id in camera_list:
                
                #print "camera id: ", camera_id
                camera = models.Camera.objects(id=camera_id).first()
                if camera is None:
                    continue
                
                prefix = "%s/"%camera_id
                for key_name in self.s3_storage.list_file(prefix):
                    # print "date: ", key_name[key_name.find("/")+1:]
                    dir_date = key_name[key_name.find("/")+1:]
                    year    = int(dir_date[:4])
                    month   = int(dir_date[4:6])
                    day     = int(dir_date[6:8])
                    dir_time = datetime.datetime(year, month, day)
                    current_time = datetime.datetime.now()
                    diff_time = current_time - dir_time
                    
                    
                    if camera.storage_periods > 0 \
                        and diff_time.days > camera.storage_periods:
#                        print "diff: ", diff_time.days
#                        print "key name: ", key_name
                        
                        self.s3_storage.delete(key_name)
                        logger.debug("delete bucket: %s key: %s " % (bucket.name, key_name) )  
                        
                        
    def __del__(self):
        logger.debug("stop " + self.name)  
'''
Created on Feb 8, 2012

@author: boatkrap
'''


import os, sys
import re, datetime
import threading, time

import boto.s3.connection
import boto.s3.key

from nokkhum import config

import logging
logger = logging.getLogger(__name__)

class S3Storage:
    def __init__(self, access_key_id, secret_access_key, host, port, secure=False):
#        logging.getLogger('boto').setLevel(logging.CRITICAL)
        self.sleep_time = 0.1
        self.connection = boto.s3.connection.S3Connection(
                        aws_access_key_id=access_key_id,
                        aws_secret_access_key=secret_access_key,
                        port=port,
                        host=host,
                        is_secure=secure,
                        calling_format=boto.s3.connection.OrdinaryCallingFormat()
                    )
        self.pattern = re.compile("__.*-(.*)-(.*)-(.*)-(.*)-(.*)-(.*)-(.*)")
        
    def __push_to_s3(self, user_id, file_list, prefix_dir):
        
        try:
            user_bucket = self.connection.get_bucket(user_id)
        except:
            try:
                self.connection.create_bucket(user_id)
                user_bucket = self.connection.get_bucket(user_id)
            except Exception as e:
                logger.exception(e)
                return
    
        prefix_dir = prefix_dir+'/'+user_id+'/'
        prefix_length = len(prefix_dir)
    
        for file_name in file_list:
            key = boto.s3.key.Key(user_bucket)
#            print file_name[prefix_length:]
            key.key = file_name[prefix_length:]
            key.set_contents_from_filename(file_name)
            logger.debug( "push %s to bucket %s key: %s complete"%(file_name,user_bucket, key.key))
            os.remove(file_name)
            # sleep for other thread run
            time.sleep(self.sleep_time)
    
    def __list_local_file(self, prefix_dir, file_list):
        extension_filter = ["avi", "png", "jpg", "ogv", "ogg", "mp4", "webm", "webp"]
#        print "list dir",os.listdir(prefix_dir)
        for i in os.listdir(prefix_dir):
#            print "i is ", i
            if os.path.isdir(prefix_dir+"/"+i):
#                print "dir: ", prefix_dir+"/"+i
                self.__list_local_file(prefix_dir+"/"+i, file_list)
            else:
                for extension in extension_filter:
                    if i[-len(extension):] == extension:
                        if "__" == i[:2]:
                            result = self.pattern.match(i)
                            if result:
                                
                                file_date = datetime.datetime(
                                        int(result.groups()[0]),
                                        int(result.groups()[1]),
                                        int(result.groups()[2]),
                                        int(result.groups()[3]),
                                        int(result.groups()[4]),
                                        int(result.groups()[5])
                                        )
                                
                                if file_date < datetime.datetime.now() - datetime.timedelta(minutes=30):
                                    os.rename(prefix_dir+"/"+i, prefix_dir+"/"+i[2:])
                            break
    
                        file_list.append(prefix_dir+"/"+i)
                        break
    
    def __empty_local_directory(self, prefix_dir):
        file_list = os.listdir(prefix_dir)
        if len(file_list) == 0:
            os.rmdir(prefix_dir)
            return
    
        for i in file_list:
            if os.path.isdir(prefix_dir+"/"+i):
                self.__empty_local_directory(prefix_dir+"/"+i)
                
        file_list = os.listdir(prefix_dir)
        if len(file_list) == 0:
            os.rmdir(prefix_dir)

    
    def push(self, prefix_dir):
       
        if not os.path.exists(prefix_dir):
            return
    
        for i in os.listdir(prefix_dir):
            if os.path.isdir(prefix_dir+"/"+i):
                file_list = []
                self.__list_local_file(prefix_dir+"/"+i, file_list)
    
                if len(file_list) > 0:
                    self.__push_to_s3(i, file_list, prefix_dir)
                    
        self.__empty_local_directory(prefix_dir)
        

class S3Thread(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        access_key_id       = config.Configurator.settings.get('nokkhum.storage.s3.access_key_id')
        secret_access_key   = config.Configurator.settings.get('nokkhum.storage.s3.secret_access_key')
        host                = config.Configurator.settings.get('nokkhum.storage.s3.host')
        port                = config.Configurator.settings.get('nokkhum.storage.s3.port')
        secure              = config.Configurator.settings.get('nokkhum.storage.s3.secure_connection')
            
        self.__s3storage = S3Storage(access_key_id, secret_access_key, host, port, secure)
        
        self.name = "S3Thread"
        self.daemon = True
        
    def run(self):
        logger.debug("start push s3 thread")
        prefix_dir = config.Configurator.settings.get('nokkhum.processor.record_path')
        self.__s3storage.push(prefix_dir)
        
    def __del__(self):
        logger.debug("end push s3 thread")
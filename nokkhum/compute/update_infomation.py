'''
Created on Nov 2, 2011

@author: boatkrap
'''

import platform
import json
import socket
import multiprocessing
import threading
import datetime
import time
import psutil
import netifaces

from . import s3

import logging
logger = logging.getLogger(__name__)

from nokkhum import config, compute

class UpdateConfiguration:
    def update(self, settings):
        logger.debug("get variable: %s"%settings)
        for variable in settings.keys():
            config.Configurator.settings[variable] = settings[variable]

class UpdateInfomation:
    def __init__(self, publisher):
        self.publisher = publisher
        try:
            self.ip = netifaces.ifaddresses(config.Configurator.settings.get('nokkhum.compute.interface')).setdefault(netifaces.AF_INET)[0]['addr']
        except:
            self.ip = netifaces.ifaddresses('lo').setdefault(netifaces.AF_INET)[0]['addr']
            
    
    def send_message(self, messages):
        try:
            self.publisher.send(messages, "nokkhum_compute.update_status")

        except Exception as e:
            logger.exception(e)
            try:
                logger.debug("reconnect publisher")
                from nokkhum.messaging import connection
                self.publisher = connection.default_connection.publisher_factory.get_publisher("nokkhum_compute.update_status")
                logger.debug("reconnect publisher success")
            except Exception as e:
                logger.exception(e)
            
            return False
            
        logging.debug("send message: %s" % messages)
        return True
    
    def get_system_information(self):
        
        mem = psutil.phymem_usage()
        system_information = {
                     'name'     : platform.node(),
                     'system'   : platform.system(),
                     'machine'  : platform.machine(),
                     'cpu_count': multiprocessing.cpu_count(),
                     'total_ram': mem.total,
                     'ip'       : self.ip,
                     }

        return system_information
    
    def update_system_information(self):
        
        arguments = self.get_system_information()
        messages = {"method": "update_system_information", "args": arguments}
        logging.debug("update information: %s" % messages)
        
        return self.send_message(messages)
        
    def get_resource(self):
        
        cpus = psutil.cpu_percent(interval=.5, percpu=True)
        
        sum = 0.0
        for usage in cpus:
            sum += usage
            
        cpu_prop = {
                    "used"     : round(sum/len(cpus)),
                    "percpu"    : cpus,
                    }
        
        mem = psutil.phymem_usage()
        mem_prop = {
                    "total" : mem.total,
                    "used"  : mem.used,
                    "free"  : mem.free
                    }
        
        disk = psutil.disk_usage(config.Configurator.settings["nokkhum.processor.record_path"])
        disk_prop = {
                     "total" : disk.total,
                     "used"  : disk.used,
                     "free"  : disk.free,
                     "percent": disk.percent,
                     }
        
        processor_manager = compute.processor_manager
        camera_list = []

        for pid, camera_id in processor_manager.get_pids():
            process = psutil.Process(pid)
            process_status = {
             'pid'          : pid,
             'camera_id'    : camera_id,
             'num_threads'  : process.get_num_threads(),
             'cpu'          : process.get_cpu_percent(interval=0.1),
             'memory'       : process.get_memory_info().rss,
             'messages'     : compute.processor_manager.read_process_output(camera_id)
            }
            
            camera_list.append(process_status)

        resource = {
                     'name'     : platform.node(),
                     'cpu'      : cpu_prop,
                     'memory'   : mem_prop,
                     'cameras'  : camera_list,
                     'disk'     : disk_prop,
                     'ip'       : self.ip,
                     'date'     : datetime.datetime.now().isoformat()
                     }
        
        
        # logging.debug("update resource: %s" % messages)
        
        return resource
        
    def update_resource(self):
        arguments = self.get_resource()
        messages = {"method": "update_resource", "args": arguments}
        return self.send_message(messages)
    
    def get_camera_running_fail(self):
        processor_manager = compute.processor_manager
        dead_process = processor_manager.remove_dead_process()
        if len(dead_process) == 0:
            return 
        
        fail_cameras = {
                     'name'         : platform.node(),
                     'ip'           : self.ip,
                     'dead_process' :dead_process,
                     'report_time'     :datetime.datetime.now().isoformat()
                     }
        
#        logging.debug("camera_running_fail_report: %s" % messages)
        return fail_cameras
    
    def camera_running_fail_report(self):
        arguments = self.get_camera_running_fail()
        if arguments == None:
            return
        messages = {"method": "camera_running_fail_report", "args":arguments}
        return self.send_message(messages)
        
class UpdateStatus(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.name = self.__class__.__name__
        self._running = False
        self.daemon = True
        self._request_sysinfo = False
        self.__s3thread = None
        
        from nokkhum.messaging import connection
        self.publisher = connection.default_connection.publisher_factory.get_publisher("nokkhum_compute.update_status")

        
    def run(self):
        time_to_sleep = 10
        update_status = False
 
        self._running = True
        
        logger.debug("start update") 
        uinfo = UpdateInfomation(self.publisher)
        
        while(self._running):
            while not update_status:
                update_status = uinfo.update_system_information()
                if not update_status:
                    logger.debug("wait controller %d second"%time_to_sleep)
                    time.sleep(time_to_sleep)
     
            while(self._running):
                #logger.debug("request_sysinfo %s"%self._request_sysinfo) 
                if self._request_sysinfo:
                    self._request_sysinfo = False
                    update_status = False
                    #logger.debug("request_sysinfo -> break") 
                    break
                
                start_time = datetime.datetime.now()
                
                try: 
                    uinfo.camera_running_fail_report()
                except Exception as e:
                    logger.exception(e)
                    
                try:
                    uinfo.update_resource()
                except Exception as e:
                    logger.exception(e)

                # sync to s3 storage
                if config.Configurator.settings.get('nokkhum.storage.enable'):
                    if config.Configurator.settings.get('nokkhum.storage.api') == "s3":
                        self.push_s3 = True
                    else:
                        self.push_s3 = False
                else:
                    uinfo.update_system_information()
                    self.push_s3 = False
                
                if self.push_s3:
                    if self.__s3thread is not None and not self.__s3thread.is_alive():
                        self.__s3thread.join()
                        self.__s3thread = None
                    
                    if self.__s3thread is None:
                        self.__s3thread = s3.S3Thread()
                        self.__s3thread.start()
                        
                end_time = datetime.datetime.now()
                
                delta = end_time - start_time
                sleep_time = time_to_sleep - delta.total_seconds()

                if sleep_time > 0:
                    time.sleep(sleep_time)
                    
    def stop(self):
        self._running = False
        
    def get_system_information(self):
        self._request_sysinfo = True
        logger.debug("request_sysinfo: %s\n"%self._request_sysinfo) 

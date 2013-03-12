'''
Created on Oct 5, 2011

@author: boatkrap
'''
import logging, time
logger = logging.getLogger(__name__)

import threading
class ProcessPolling(threading.Thread):
    def __init__(self, processor, output_list):
        self.processor=processor
        self.output_list = output_list
        self.running = True
        super().__init__()
        
    def run(self):
        time.sleep(5)
        while self.running:
            data = self.processor.process.stderr.readline().decode('utf-8')
            self.output_list.append(data)
            

class ProcessorManager:
    def __init__(self):
        self.pool = dict()
        self.thread_pool = dict()
        self.output = dict()
        
    def add(self, camera_id, processor):
        if not camera_id in self.pool.keys():
            self.pool[camera_id] = processor
            self.output[camera_id] = []
            self.thread_pool[camera_id] = ProcessPolling(processor, self.output[camera_id])
            self.thread_pool[camera_id].start()
            
    def delete(self, camera_id):
        if camera_id in self.pool.keys():
            del self.pool[camera_id]
            
            self.thread_pool[camera_id].running = False
            del self.thread_pool[camera_id]
            
            del self.output[camera_id]
            
    def get(self, camera_id):
        if camera_id in self.pool.keys():
            return self.pool[camera_id]
        else:
            return None
        
    def get_pool(self):
        return self.pool
        
    def list_camera(self):
        return self.pool.keys()
    
    def available(self):
        avialable_process = []
        for k, v in self.pool.items():
            if v.is_running():
                avialable_process.append(k)
                
        return avialable_process
    
    def read_process_output(self, camera_id):
        results=[]
        
        if int(camera_id) in self.pool.keys():
            while len(self.output[camera_id]) > 0 :
                logger.debug("camera id: %d" % camera_id)
                results.append(self.output[camera_id].pop())
        
        return results

    def remove_dead_process(self):
        dead_process = {}
        
        remove_process = [k for k, v in self.pool.items() if not v.is_running()]
        
        # try to remove dead process
        for key in remove_process:
            camera_process = self.pool[key]
            if not camera_process.is_running():
                result=""
                try:
                    for line in camera_process.process.stdout:
                        result += line.decode('utf-8')
                    for line in camera_process.process.stderr:
                        result += line.decode('utf-8')
                except Exception as e:
                    logger.exception(e)
                    
                if len(result)==0:
                    result = "Process exist with Unknown Message"
                dead_process[key] = result
                self.delete(key)
                
        
        logger.debug("remove: %s", dead_process)
        return dead_process
    
    def get_pids(self):
        pids = []
        for k, v in self.pool.items():
            pids.append((v.process.pid, k))
            
        return pids
'''
Created on Dec 23, 2011

@author: boatkrap
'''

import threading, datetime, time

from nokkhum.messaging import consumer, connection
import logging

from nokkhum import models
from nokkhum import config

logger = logging.getLogger(__name__)

class ComputeNodeResource:
    
    def initial_central_configuration(self, host):
        storage_settings={}
        
        for setting in config.settings.keys():
            if 'nokkhum.storage' in setting:
                storage_settings[setting] = config.settings.get(setting)
                
        routing_key = "nokkhum_compute."+host.replace('.', ':')+".rpc_request"
        message={"method":"update_system_configuration"}
        
        message['args'] = dict(settings=storage_settings)
        
        logger.debug('update storage to : "%s" message: %s routing_key: %s' % (host, message, routing_key))
        rpc_client = connection.default_connection.get_rpc_factory().get_default_rpc_client()
        rpc_client.send(message, routing_key)
        
            

    def update_system_information(self, args):
        try:
            name        = args['name']
            cpu_count   = args['cpu_count']
            total_ram   = args['total_ram']
            system      = args['system']
            machine     = args['machine']
            host        = args['ip']
            
            compute_node = models.ComputeNode.objects(host=host).first()
            logger.debug("compute node: %s"% compute_node)
            if compute_node is None:
                compute_node = models.ComputeNode()
                compute_node.create_date = datetime.datetime.now()
                compute_node.host = host
                
            cpu = models.CPUInfomation()
            cpu.count = cpu_count
            
            memory = models.MemoryInfomation()
            memory.total = total_ram
            
            compute_node.name    = name
            compute_node.machine = machine
            compute_node.system  = system
            compute_node.cpu     = cpu
            compute_node.memory  = memory
            compute_node.update_date = datetime.datetime.now()
            compute_node.save()
        
            logger.debug( 'Compute node name: "%s" update system info complete' % ( name ) )
        except Exception as e:
            logger.exception(e)        

    def update_resource(self, args):
        try:
            name        = args['name']
            cpu         = args['cpu']
            memory      = args['memory']
            cameras     = args['cameras']
            host        = args['ip']
            report_date = datetime.datetime.strptime(args['date'], '%Y-%m-%dT%H:%M:%S.%f')       
            
            compute_node = models.ComputeNode.objects(host=host).first()
            
            if compute_node is None \
                or datetime.datetime.now() - compute_node.update_date > datetime.timedelta(seconds=30):
                
                routing_key = "nokkhum_compute."+host.replace('.', ':')+".rpc_request"
                message={"method":"get_system_information"}
                
                rpc_client = connection.default_connection.get_rpc_factory().get_default_rpc_client()
                rpc_client.send(message, routing_key)
                logger.debug('compute node: "%s" unavailable. push %s by routing key: %s' % (name, message, routing_key))
                
                if compute_node is None:
                    return 
            
            compute_node.cpu.usage   = cpu["usage"]
            compute_node.cpu.usage_per_cpu = cpu["percpu"]
            
            compute_node.memory.total = memory["total"]
            compute_node.memory.used  = memory["used"]
            compute_node.memory.free  = memory["free"]
            
            current_time = datetime.datetime.now()
            compute_node.update_date = current_time
            compute_node.save()

            report              = models.ComputeNodeReport()
            report.compute_node = compute_node
            report.report_date  = report_date
            report.cpu          = compute_node.cpu
            report.memory       = compute_node.memory
            
            for camera_process in cameras:
                camera = models.Camera.objects().get(id=camera_process['camera_id'])
                camera.operating.status = "Running"
                camera.operating.update_date = current_time
                camera.operating.compute_node = compute_node
                camera.save()
                
                cps = models.CameraProcessStatus()
                cps.camera  = camera
                cps.cpu     = camera_process['cpu']
                cps.memory  = camera_process['memory']
                cps.threads = camera_process['num_threads']
                
                report.camera_process_status.append(cps)
                
            report.save()
                
            logger.debug( 'Compute node name: "%s" ip: %s update resource complete' % ( name, host ) )
        except Exception as e:
            logger.exception(e)

    def camera_running_fail_report(self, args):
        try:
            name        = args['name']
            host        = args['ip']
            dead_process= args['dead_process'] 
            report_time = datetime.datetime.strptime(args['report_time'], '%Y-%m-%dT%H:%M:%S.%f')
            compute_node = models.ComputeNode.objects(name=name, host=host).first()
        except Exception as e:
            logger.exception(e)  
            return
        
        for camera_id, message in dead_process.items():
            camera = models.Camera.objects(id=int(camera_id)).first()
            if not camera:
                return
            
            camera_status = models.CameraRunningFail()
            camera_status.camera = camera
            camera_status.compute_node = compute_node
            camera_status.message = message
            camera_status.report_time = report_time
            camera_status.process_time = datetime.datetime.now()
            camera_status.save()
            
            camera.operating.status = "Fail"
            camera.operating.update_date = datetime.datetime.now()
            camera.save()
            
            logger.debug( 'Compute node name: "%s" ip: %s got camera error id: %s msg:\n %s' % ( name, host, camera_id, message) )
        

class UpdateStatus(threading.Thread):
    
    def __init__(self):
        threading.Thread.__init__(self)
        self.name = self.__class__.__name__
        self._consumer = connection.default_connection.consumer_factory.get_consumer("nokkhum_compute.update_status")
        self._consumer.register_callback(self.process_msg)
        self.daemon = True
        self._running = False
        self._cn_resource = ComputeNodeResource()
        
    def process_msg(self, body, message):
        if "method" not in body:
            logger.debug("ignore message", body)
            message.ack()
            return
        #logger.debug("controller get message: %s" % body)
        if body["method"] == "update_system_information":
            self._cn_resource.update_system_information(body["args"])
            self._cn_resource.initial_central_configuration(body["args"]['ip'])
        elif body["method"] == "update_resource":
            self._cn_resource.update_resource(body["args"])
        elif body["method"] == "camera_running_fail_report":
            self._cn_resource.camera_running_fail_report(body["args"])
        message.ack()

    def run(self):
        self._running = True
        while self._running:
#            now = datetime.datetime.now()
#            if now.minute == 0 and (now.second >= 0 and now.second <= 13):
#                compute_nodes = models.ComputeNode.objects(update_date__gt=now-datetime.timedelta(minutes=10)).all()
#                for compute_node in compute_nodes:
#                    self._cn_resource.initial_central_configuration(compute_node.host)
                    
            time.sleep(10)

            
    def stop(self):
        self._running = False

    
    
    
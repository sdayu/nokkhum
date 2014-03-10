'''
Created on Dec 23, 2011

@author: boatkrap
'''

import threading, datetime, time, json

from nokkhum.messaging import connection
import logging

from nokkhum import models
from nokkhum import config



logger = logging.getLogger(__name__)

class ComputeNodeResource:
    
    def initial_central_configuration(self, host):
        storage_settings={}
        
        for setting in config.Configurator.settings.keys():
            if 'nokkhum.storage' in setting:
                storage_settings[setting] = config.Configurator.settings.get(setting)
                
        routing_key = "nokkhum_compute."+host.replace('.', ':')+".rpc_request"
        message={"method":"update_system_configuration"}
        
        message['args'] = dict(settings=storage_settings)
        
        logger.debug('update storage to : "%s" message: %s routing_key: %s' % (host, message, routing_key))
        rpc_client = connection.Connection.get_instance().get_rpc_factory().get_default_rpc_client()
        rpc_client.send(message, routing_key)

    def update_system_information(self, args):
        try:
            name        = args['name']
            cpu_count   = args['cpu_count']
            cpu_frequency = args['cpu_frequency']
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
                
            cpu = models.CPUInformation()
            cpu.count = cpu_count
            cpu.frequency = cpu_frequency
            
            memory = models.MemoryInformation()
            memory.total = total_ram
            
            compute_node.name    = name
            compute_node.machine = machine
            compute_node.system  = system
            compute_node.cpu     = cpu
            compute_node.memory  = memory
            compute_node.update_date = datetime.datetime.now()
            if 'response_date' not in compute_node.extra:
                compute_node.extra['response_date'] = list()

            compute_node.extra['response_date'].append(datetime.datetime.now())
            compute_node.save()
        
            logger.debug( 'Compute node name: "%s" update system info complete' % ( name ) )
            
            rpc_client = connection.Connection.get_instance().get_rpc_factory().default_rpc_client
            if rpc_client is not None:
                routing_key = "nokkhum_compute.%s.rpc_request"%compute_node.host.replace(".", ":")
                rpc_client._publisher.drop_routing_key(routing_key)
        except Exception as e:
            logger.exception(e)        

    def update_resource(self, args):
        try:
            name        = args['name']
            cpu         = args['cpu']
            memory      = args['memory']
            disk        = args['disk']
            processors  = args['processors']
            host        = args['ip']
            report_date = datetime.datetime.strptime(args['date'], '%Y-%m-%dT%H:%M:%S.%f')       
            
            compute_node = models.ComputeNode.objects(host=host).first()
            
            if compute_node is None \
                or datetime.datetime.now() - compute_node.update_date > datetime.timedelta(seconds=30):
                
                routing_key = "nokkhum_compute."+host.replace('.', ':')+".rpc_request"
                message={"method":"get_system_information"}
                
                rpc_client = connection.Connection.get_instance().get_rpc_factory().get_default_rpc_client()
                rpc_client.send(message, routing_key)
                logger.debug('compute node: "%s" unavailable. push %s by routing key: %s' % (name, message, routing_key))
                
                if compute_node is None:
                    return 
            
            compute_node.cpu.used   = cpu["used"]
            compute_node.cpu.used_per_cpu = cpu["percpu"]
            
            compute_node.memory.total = memory["total"]
            compute_node.memory.used  = memory["used"]
            compute_node.memory.free  = memory["free"]
            
            compute_node.disk.total = disk['total']
            compute_node.disk.used = disk['used']
            compute_node.disk.free = disk['free']
            compute_node.disk.percent = disk['percent']
            
            current_time = datetime.datetime.now()
            compute_node.update_date = current_time
            compute_node.save()

            report              = models.ComputeNodeReport()
            report.compute_node = compute_node
            report.report_date  = report_date
            report.cpu          = compute_node.cpu
            report.memory       = compute_node.memory
            report.disk         = compute_node.disk
            report.save()
            
            for processor_process in processors:
                processor = models.Processor.objects().with_id(processor_process['processor_id'])
                processor.operating.status = "running"
                processor.operating.update_date = current_time
                processor.operating.compute_node = compute_node
                processor.save()
                
                ps = models.ProcessorStatus()
                ps.processor  = processor
                ps.report_date = report_date
                ps.cpu     = processor_process['cpu']
                ps.memory  = processor_process['memory']
                ps.threads = processor_process['num_threads']
                ps.messages = processor_process['messages']
                ps.compute_node_report = report
                ps.save()
                
                report.processor_status.append(ps)
                
                for message in processor_process['messages']:
                    try:
                        processor_message = json.loads(message)
                        if 'method' in processor_message:
                            if processor_message["method"] == "notify":

                                logger.debug("get notification")
                                from nokkhum.controller import notification
                                try:
                                    email = notification.EmailNotification()
                                    email.send_mail(processor.id)
                                except Exception as e:
                                    logger.exception(e)
                            if processor_message["method"] == "face_detected":
                                tmp = model.Notification()
                                tmp.method      =  processor_message["method"]
                                tmp.camera      =  processor_message["camera_id"]
                                tmp.description =  processor_message["description"]
                                tmp.filename    =  processor_message["filename"]
                                tmp.face_name   =  processor_message["face_name"]
                                tmp.save()
                            if processor_message["method"] == "motion_detected":
                                tmp = model.Notification()
                                tmp.method = processor_message["method"]
                                tmp.camera = processor_message["camera_id"]
                                tmp.description = processor_message["description"]
                                tmp.face_name = processor_message["area"]
                                tmp.filename = "";
                                tmp.save()


                    except:
                        logger.exception("fail load json: %s"% message)
                    
            report.save()
                
            logger.debug( 'Compute node name: "%s" ip: %s update resource complete' % ( name, host ) )
        except Exception as e:
            logger.exception(e)

    def processor_run_fail_report(self, args):
        try:
            name        = args['name']
            host        = args['ip']
            dead_process= args['dead_process'] 
            report_time = datetime.datetime.strptime(args['report_time'], '%Y-%m-%dT%H:%M:%S.%f')
            compute_node = models.ComputeNode.objects(name=name, host=host).first()
        except Exception as e:
            logger.exception(e)  
            return
        
        logger.debug("controller get processor fail: %s" % args)
        
        for processor_id, message in dead_process.items():
            processor = models.Processor.objects().with_id(processor_id)
            if not processor:
                return
            
            processor_status = models.ProcessorRunFail()
            processor_status.processor = processor
            processor_status.compute_node = compute_node
            processor_status.message = message
            processor_status.report_time = report_time
            processor_status.process_time = datetime.datetime.now()
            processor_status.save()
            
            processor.operating.status = "fail"
            processor.operating.update_date = datetime.datetime.now()
            processor.save()
            
            logger.debug( 'Compute node name: "%s" ip: %s got processor error id: %s msg:\n %s' % ( name, host, processor_id, message) )
        

class UpdateStatus(threading.Thread):
    
    def __init__(self, consumer=None):
        threading.Thread.__init__(self)
        self.name = self.__class__.__name__
        self.daemon = True
        self._running = False
        self._consumer = consumer
        self._cn_resource = ComputeNodeResource()
    
    def set_consumer(self, consumer):
        self._consumer = consumer
        self._consumer.register_callback(self.process_msg)
        
        
    def process_msg(self, body, message):
        if "method" not in body:
            logger.debug("ignore message", body)
            message.ack()
            return
        
        # logger.debug("controller get message: %s" % body)
        if body["method"] == "update_system_information":
            self._cn_resource.update_system_information(body["args"])
            self._cn_resource.initial_central_configuration(body["args"]['ip'])
        elif body["method"] == "update_resource":
            self._cn_resource.update_resource(body["args"])
        elif body["method"] == "processor_run_fail_report":
            self._cn_resource.processor_run_fail_report(body["args"])
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

    
    
    

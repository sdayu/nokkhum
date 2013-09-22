'''
Created on Jan 9, 2012

@author: boatkrap
'''

import netifaces
from nokkhum.messaging import consumer, connection

import logging
logger = logging.getLogger(__name__)

from nokkhum import compute, config
from nokkhum.compute.update_infomation import UpdateStatus, UpdateConfiguration


class ComputeApi():
    
    def __init__(self):
        
        self.daemon = True
        self._running = False
        self.update_status = UpdateStatus() 
        
        ip = "127.0.0.1"
        try:
            ip = netifaces.ifaddresses(config.Configurator.settings.get('nokkhum.compute.interface')).setdefault(netifaces.AF_INET)[0]['addr']
        except Exception as e:
            logger.exception(e)
            ip = netifaces.ifaddresses('lo').setdefault(netifaces.AF_INET)[0]['addr']
        
#        routing_key = "nokkhum_compute."+self.ip.replace('.', ":")+".rpc_request"
#        self._consumer = consumer.ConsumerFactory().get_consumer(routing_key)

        from nokkhum.messaging import connection
        self.rpc = connection.default_connection.get_rpc_factory().get_default_rpc_server(ip)
        self.rpc.register_callback(self.process_msg)
        
        from .processors import processor_controller
        self.processor_controller = processor_controller.ProcessorController()
        
    def process_msg(self, body, message):
        logger.debug("get command: %s"%body)
        # message.ack()
        if 'method' not in body:
            logger.debug("ignore message: %s"%body)
        elif body['method'] == 'get_system_information':
            self.update_status.get_system_information()
            logger.debug(" self.rpc._publisher.routing_key_list %s"% self.rpc._publisher.routing_key_list)
            self.rpc._publisher.routing_key_list.clear()
            
        elif body['method'] == 'update_system_configuration':
            settings=body['args']['settings']
            UpdateConfiguration().update(settings)
        else:
            if 'message_id' in body:
                
                respons = None
                if body['method'] == 'list_processors':
                    respons = self.processor_controller.list_processors()
                elif body['method'] == 'get_processor_attributes':
                    respons = self.processor_controller.get_processor_attributes(body['args']['processor_id'])
                elif body['method'] == 'start_processor':
                    respons = self.processor_controller.start_processor(body['args']['processor_id'], body['args']['attributes'])
                elif body['method'] == 'stop_processor':
                    respons = self.processor_controller.stop_processor(body['args']['processor_id'])
                
                respons['message_id'] = body['message_id']
                self.rpc.reply(respons, body['reply_to'])
                logger.debug("reply_to %s "%body['reply_to'])
                logger.debug("response command: %s"%respons)
        logger.debug("success process command")
        message.ack()
        

        
    def start(self):
        self.update_status.start()
        self._running = True
        while self._running:
            # logger.debug("drain event")
            if not self.update_status.is_alive():
                self.update_status.join()
                self.update_status = UpdateStatus() 
                self.update_status.start()
            connection.default_connection.drain_events()
            
    def stop(self):
        self._running = False
        self.update_status.stop()
        connection.default_connection.release()
        logger.debug("start to stop all cameras")
        self.processor_controller.stop_all()
        logger.debug("end to stop all cameras")

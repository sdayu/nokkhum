'''
Created on Nov 7, 2011

@author: boatkrap
'''

import logging
logger = logging.getLogger(__name__)

from nokkhum.messaging import connection
import netifaces
from nokkhum import config
from nokkhum.controller.camera import CameraAttributesBuilder

class ProcessorManager:
    def __init__(self):
        #self.rpc = connection.default_connection.get_rpc_factory().get_default_rpc_client()
        
        ip = "127.0.0.1"
        try:
            ip = netifaces.ifaddresses(config.Configurator.settings.get('nokkhum.controller.interface')).setdefault(netifaces.AF_INET)[0]['addr']
        except Exception as e:
            logger.exception(e)
            ip = netifaces.ifaddresses('lo').setdefault(netifaces.AF_INET)[0]['addr']
    
        self.rpc = connection.default_connection.get_rpc_factory().get_default_rpc_client(ip)
        
    def __get_routing_key(self, ip):
        return "nokkhum_compute."+ip.replace('.', ':')+".rpc_request"
    
    def __call_rpc(self, request, routing_key):
        logger.debug("send request routing key: %s \nmessage: %s"%(routing_key, request))
        return self.rpc.call(request, routing_key)
    
    def start_processor(self, compute_node, camera):

        camera_attribute = CameraAttributesBuilder(camera).get_attribute()        
        
        args = {
                'processor_id': str(camera.id),
                'attributes': camera_attribute,
                }
        request = {
                   'method': 'start_processor',
                   'args': args,
                   }
        
        return self.__call_rpc(request, self.__get_routing_key(compute_node.host))
        
    def stop_processor(self, compute_node, camera):
        request = {
                   'method': 'stop_processor',
                   'args': {'camera_id': str(camera.id)}
                   }
        
        return self.__call_rpc(request, self.__get_routing_key(compute_node.host))
        
    def list_processor(self, compute_node):
        request = {
                   'method': 'list_processors',
                   }
        
        return self.__call_rpc(request, self.__get_routing_key(compute_node.host))
        
    def get_processor_attribute(self, compute_node, camera):
        request = {
                   'method': 'get_processor_attributes',
                   'args': {'camera_id': str(camera.id)}
                   }
        
        return self.__call_rpc(request, self.__get_routing_key(compute_node.host))
'''
Created on Nov 7, 2011

@author: boatkrap
'''

import logging
logger = logging.getLogger(__name__)

from nokkhum.messaging import connection
import netifaces
from nokkhum import config

class ProcessorAttributesBuilder:
    def __init__(self, processor):
        self.processor=processor
        
    def get_camera_attribute(self):
        result = []
        for camera in self.processor.cameras:
            size = camera.image_size.split("x")
            camera_att = dict(
                      id = str(camera.id),
                      name = camera.name,
                      model = camera.camera_model.name,
                      username = camera.username,
                      password = camera.password,
                      fps = camera.fps,
                      width = int(size[0]),
                      height = int(size[1]),
                      video_uri = camera.video_uri,
                      audio_uri = camera.audio_uri,
                      image_uri = camera.image_uri
                    )
            result.append(camera_att)
        return result
    
    def get_attribute(self):

        attributes = dict()
        attributes["cameras"] = self.get_camera_attribute()
        attributes["image_processors"] = self.processor.image_processors
        
        return attributes


class ProcessorManager:
    def __init__(self):
        #self.rpc = connection.default_connection.get_rpc_factory().get_default_rpc_client()
        
        ip = "127.0.0.1"
        try:
            ip = netifaces.ifaddresses(config.Configurator.settings.get('nokkhum.controller.interface')).setdefault(netifaces.AF_INET)[0]['addr']
        except Exception as e:
            logger.exception(e)
            ip = netifaces.ifaddresses('lo').setdefault(netifaces.AF_INET)[0]['addr']
    
        self.rpc = connection.Connection.get_instance().get_rpc_factory().get_default_rpc_client(ip)
        
    def __get_routing_key(self, ip):
        return "nokkhum_compute."+ip.replace('.', ':')+".rpc_request"
    
    def __call_rpc(self, request, routing_key):
        logger.debug("send request routing key: %s \nmessage: %s"%(routing_key, request))
        return self.rpc.call(request, routing_key)
    
    def start_processor(self, compute_node, processor):

        processor_attribute = ProcessorAttributesBuilder(processor).get_attribute()        
        
        args = {
                'processor_id': str(processor.id),
                'attributes': processor_attribute,
                }
        request = {
                   'method': 'start_processor',
                   'args': args,
                   }
        
        return self.__call_rpc(request, self.__get_routing_key(compute_node.host))
        
    def stop_processor(self, compute_node, processor):
        request = {
                   'method': 'stop_processor',
                   'args': {'processor_id': str(processor.id)}
                   }
        
        return self.__call_rpc(request, self.__get_routing_key(compute_node.host))
        
    def list_processor(self, compute_node):
        request = {
                   'method': 'list_processors',
                   }
        
        return self.__call_rpc(request, self.__get_routing_key(compute_node.host))
        
    def get_processor_attribute(self, compute_node, processor):
        request = {
                   'method': 'get_processor_attributes',
                   'args': {'processor_id': str(processor.id)}
                   }
        
        return self.__call_rpc(request, self.__get_routing_key(compute_node.host))
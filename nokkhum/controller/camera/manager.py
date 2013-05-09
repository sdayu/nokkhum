'''
Created on Nov 7, 2011

@author: boatkrap
'''

import logging
logger = logging.getLogger(__name__)

class CameraAttributesBuilder:
    def __init__(self, camera):
        self.camera=camera
        
    def get_attribute(self):
        
        size = self.camera.image_size.split("x")
        
        camera_att = dict()
        camera_att["id"]        = str(self.camera.id)
        camera_att["name"]      = self.camera.name
        camera_att["model"]     = self.camera.camera_model.name
        camera_att["username"]  = self.camera.username
        camera_att["password"]  = self.camera.password
        camera_att["fps"]       = self.camera.fps
        camera_att["width"]     = int(size[0])
        camera_att["height"]    = int(size[1])
        camera_att["video_url"]       = self.camera.video_url
        camera_att["audio_url"]       = self.camera.audio_url
        camera_att["image_url"]       = self.camera.image_url

        
        attributes = dict()
        attributes["camera"] = camera_att
        attributes["processors"] = self.camera.processors
        return attributes



from nokkhum.messaging import connection
import netifaces
from nokkhum import config

class CameraManager:
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
    
    def start_camera(self, compute_node, camera):

        camera_attribute = CameraAttributesBuilder(camera).get_attribute()        
        
        args = {
                'camera_id': str(camera.id),
                'attributes': camera_attribute,
                }
        request = {
                   'method': 'start_camera',
                   'args': args,
                   }
        
        return self.__call_rpc(request, self.__get_routing_key(compute_node.host))
        
    def stop_camera(self, compute_node, camera):
        request = {
                   'method': 'stop_camera',
                   'args': {'camera_id': str(camera.id)}
                   }
        
        return self.__call_rpc(request, self.__get_routing_key(compute_node.host))
        
    def list_camera(self, compute_node):
        request = {
                   'method': 'list_camera',
                   }
        
        return self.__call_rpc(request, self.__get_routing_key(compute_node.host))
        
    def get_camera_attribute(self, compute_node, camera):
        request = {
                   'method': 'get_cameras_attributes',
                   'args': {'camera_id': str(camera.id)}
                   }
        
        return self.__call_rpc(request, self.__get_routing_key(compute_node.host))
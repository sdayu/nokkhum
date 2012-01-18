'''
Created on Nov 7, 2011

@author: boatkrap
'''

import urllib, urllib2
import json

class CameraAttributesBuilder:
    def __init__(self, camera):
        self.camera=camera
        
    def get_attribute(self):
        
        size = self.camera.image_size.split("x")
        
        camera_att = dict()
        camera_att["id"]        = self.camera.id
        camera_att["name"]      = self.camera.name
        camera_att["model"]     = self.camera.camera_model.name
        camera_att["username"]  = self.camera.username
        camera_att["password"]  = self.camera.password
        camera_att["fps"]       = self.camera.fps
        camera_att["width"]     = int(size[0])
        camera_att["height"]    = int(size[1])
        camera_att["url"]       = self.camera.url

        
        attributes = dict()
        attributes["camera"] = camera_att
        attributes["processors"] = self.camera.processors
        return attributes

from nokkhum.common.messaging import connection
class CameraManager:
    def __init__(self):
        self.rpc = connection.default_connection.get_rpc_factory().get_default_rpc_client()
        
    def __get_routing_key(self, ip):
        return "nokkhum_compute."+ip.replace('.', ':')+".rpc_request"
    
    def start_camera(self, compute_node, camera):

        camera_attribute = CameraAttributesBuilder(camera).get_attribute()        
        
        args = {
                'camera_id': camera.id,
                'attributes': camera_attribute,
                }
        request = {
                   'method': 'start_camera',
                   'args': args,
                   }
        
        return self.rpc.call(request, self.__get_routing_key(compute_node.host))
        
    def stop_camera(self, compute_node, camera):
        request = {
                   'method': 'stop_camera',
                   'args': {'camera_id': camera.id}
                   }
        
        return self.rpc.call(request, self.__get_routing_key(compute_node.host))
        
    def list_camera(self, compute_node):
        request = {
                   'method': 'list_camera',
                   }
        
        return self.rpc.call(request, self.__get_routing_key(compute_node.host))
        
    def get_camera_attribute(self, compute_node, camera):
        request = {
                   'method': 'get_cameras_attributes',
                   'args': {'camera_id': camera.id}
                   }
        
        return self.rpc.call(request, self.__get_routing_key(compute_node.host))
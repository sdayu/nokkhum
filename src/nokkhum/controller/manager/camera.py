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
        
        size = self.camera.image_size.splite("x")
        
        camera_att = dict()
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

class CameraManager:
    def __init__(self):
        self.http = "http"
        self.start_camera_url = "/camera/start"
        self.stop_camera_url = "/camera/stop"
        self.list_camera_url = "/camera/list"
        self.get_attribute_camera_url = "/camera/get_attributes"
        
    def start_camea(self, compute_node, camera):
        
        url =  "%s://%s:%d%s" % (self.http, compute_node.host, compute_node.port, self.start_camera_url)

        camera_attribute = CameraAttributesBuilder(camera).get_attribute()        
        output = urllib2.urlopen(url, urllib.urlencode({'camera_id':camera.id, 'attributes': json.dumps(camera_attribute)}))
        print json.loads(output.read())
        
    def stop_camera(self, compute_node, camera):
        url =  "%s://%s:%d%s" % (self.http, compute_node.host, compute_node.port, self.stop_camera_url)
        output = urllib2.urlopen(url, urllib.urlencode({'camera_id': camera.id}))
        print json.loads(output.read())
        
    def list_camera(self, compute_node):
        url =  "%s://%s:%d%s" % (self.http, compute_node.host, compute_node.port, self.list_camera_url)
        output = urllib2.urlopen(url)
        print json.loads(output.read())
        
    def get_camera_attribute(self, compute_node, camera):
        url =  "%s://%s:%d%s" % (self.http, compute_node.host, compute_node.port, self.get_attribute_camera_url)
        output = urllib2.urlopen(url, urllib.urlencode({'camera_id':camera.id}))
        print json.loads(output.read())
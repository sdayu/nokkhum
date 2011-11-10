'''
Created on Nov 7, 2011

@author: boatkrap
'''

import urllib, urllib2
import json

class CameraManager(object):
    def __init__(self):
        self.http = "http"
        self.start_camera_url = "/camera/start"
        self.stop_camera_url = "/camera/stop"
        self.list_camera_url = "/camera/list"
        self.get_attribute_camera_url = "/camera/get_attributes"
        
    def startCamea(self, compute_node, camera):
        
        url = self.http + "://" + compute_node.host + ":" + compute_node.port + self.start_camera_url
        
        camera_attribute = {}
        
        output = urllib2.urlopen(url, urllib.urlencode({'camera_id':camera.id, 'attributes': json.dumps(camera_attribute)}))
        print json.loads(output.read())
        
    def stopCamera(self, compute_node, camera):
        url = self.http + "://" + compute_node.host + ":" + compute_node.port + self.stop_camera_url
        output = urllib2.urlopen(url, urllib.urlencode({'camera_id': camera.id}))
        print json.loads(output.read())
        
    def listCamera(self, compute_node):
        url = self.http + "://" + compute_node.host + ":" + compute_node.port + self.list_camera_url
        output = urllib2.urlopen(url)
        print json.loads(output.read())
        
    def getCameraAttribute(self, compute_node, camera):
        url = self.http + "://" + compute_node.host + ":" + compute_node.port + self.get_attribute_camera_url
        output = urllib2.urlopen(url, urllib.urlencode({'camera_id':camera.id}))
        print json.loads(output.read())
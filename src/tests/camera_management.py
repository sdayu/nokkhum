'''
Created on Oct 31, 2011

@author: boatkrap
'''
import unittest


class CameraManagementTest(unittest.TestCase):


    def testStartCamera(self):
        import json, urllib, urllib2
        camera_attribute = {
            "camera":    {
                "name":"Camera 1",
                "model":"Logitech",
                "fps":10,
                "width":640,
                "height":480,
                "url":"rtsp://172.30.143.249/play1.sdp",
                "username":"",
                "password":""
            },
    
            "processors":[
                {
                    "name":"Motion Detector",
                    "interval":3,
                    "resolution":98,
                    "processors":[
                        {
                            "name":"Video Recorder",
                            "fps":10,
                            "directory":"/tmp",
                            "width":640,
                            "height":480,
                            "record_motion":True,
                            "maximum_wait_motion":1
                        },
                        {
                            "name":"Face Detector",
                            "interval":5,
                            "processors":[
                                {
                                    "name":"Image Recorder",
                                    "directory":"/tmp",
                                    "width":640,
                                    "height":480
                                }
                            ]
                         }
                    ]
                 },        
                {
                    "name":"Video Recorder",
                    "fps":10,
                    "directory":"/tmp",
                    "width":640,
                    "height":420,
                }
            ]
        }
        
        import time
        print "try to start camera 1"
        output = urllib2.urlopen('http://localhost:9000/camera/start', urllib.urlencode({'camera_id':"test-1", 'attributes': json.dumps(camera_attribute)}))
        print json.loads(output.read())
        
        print "sleep 60 1"
        time.sleep(60)
        print "try to start camera 2"
        camera_attribute["camera"]["name"] = "camera 2"
        output = urllib2.urlopen('http://localhost:9000/camera/start', urllib.urlencode({'camera_id':"test-2", 'attributes': json.dumps(camera_attribute)}))
        print json.loads(output.read())
        
        print "sleep 60 2"
        time.sleep(60)
        print "try to start again"
        output = urllib2.urlopen('http://localhost:9000/camera/start', urllib.urlencode({'camera_id':"test-1", 'attributes': json.dumps(camera_attribute)}))
        print json.loads(output.read())
    
        print "try to list"
        output = urllib2.urlopen('http://localhost:9000/camera/list')
        print json.loads(output.read())
        
        print "try to get attribute"
        output = urllib2.urlopen('http://localhost:9000/camera/get_attributes', urllib.urlencode({'camera_id':"test-1"}))
        print json.loads(output.read())
        
        print "sleep 100"
        time.sleep(100)
        
        print "stop test-1"
        output = urllib2.urlopen('http://localhost:9000/camera/stop', urllib.urlencode({'camera_id': "test-1"}))
        print json.loads(output.read())
        
        print "sleep 60 3"
        time.sleep(60)
        
        print "try to list"
        output = urllib2.urlopen('http://localhost:9000/camera/list')
        print json.loads(output.read())
        
        print "stop test-2"
        output = urllib2.urlopen('http://localhost:9000/camera/stop', urllib.urlencode({'camera_id': "test-2"}))
        print json.loads(output.read())



if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testStartCamera']
    unittest.main()
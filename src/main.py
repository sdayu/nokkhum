'''
Created on Sep 7, 2011

@author: boatkrap
'''
import json

if __name__ == '__main__':
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

    output = urllib2.urlopen('http://localhost:9000/camera/start', urllib.urlencode({'attributes': json.dumps(camera_attribute), 'camera_id':"test-1"}))
    print json.loads(output.read())
    

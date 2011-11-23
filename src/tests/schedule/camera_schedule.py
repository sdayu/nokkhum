'''
Created on Nov 23, 2011

@author: boatkrap
'''
import unittest
from nokkhum import controller, model
from nokkhum.controller import schedule
import ConfigParser

class Test(unittest.TestCase):


    def testCameraScheduling(self):
        config = ConfigParser.ConfigParser()
        config.read("../../configuration.ini")
        
        controller.config = config
        setting = dict()
        for k, v in config.items("controller"):
            setting[k] = v
        
        model.initial(setting)   
    
        scheding = schedule.camera.CameraScheduling()
        scheding.run()


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testCameraScheduling']
    unittest.main()
'''
Created on Jul 9, 2012

@author: boatkrap
'''
import unittest
from nokkhum import controller, models
import ConfigParser

class Test(unittest.TestCase):


    def setUp(self):
        config_file = "../../configuration.ini"
        config = ConfigParser.ConfigParser()
        config.read(config_file)
        
        controller.config = config
        setting = dict()
        for k, v in config.items("controller"):
            setting[k] = v
        
        models.initial(setting)   
        
        import logging.config
        logging.config.fileConfig(config_file)
        

    def tearDown(self):
        pass


    def testName(self):
        from nokkhum.controller.manager import storage
        storage_thread = storage.Storage()
        storage_thread.start()
        storage_thread.join()


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
'''
Created on Jul 13, 2012

@author: boatkrap
'''
import unittest
from nokkhum import controller, models
import ConfigParser
import os

from nokkhum.cloud.vm import ec2

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
        
        log_path = setting["nokkhum.controller.log_dir"]
        if not os.path.exists(log_path):
            os.mkdir(log_path)
        
        import logging.config
        logging.config.fileConfig(config_file)
        access_key_id       = config.get('controller', "nokkhum.ec2.access_key_id")
        secret_access_key   = config.get('controller', "nokkhum.ec2.secret_access_key")
        host    = config.get('controller', "nokkhum.ec2.host")
        port    = config.getint('controller', "nokkhum.ec2.port")
        secure  = config.getboolean('controller', "nokkhum.ec2.secure_connection")
#        region_name= setting["nokkhum.ec2.region_name"]
#        path= setting["nokkhum.ec2.path"]
        
        print "host:", host
        print "port:", port
        print "secure:", secure
        self.ec2 = ec2.EC2Client(access_key_id, secret_access_key, host, port, secure)


    def tearDown(self):
        pass


    def testListImage(self):
        images = self.ec2.get_all_images()
        for image in images:
            print 'image:',image.name, "location:", image.location
    
    def testListInstance(self):
        reservations = self.ec2.get_all_instances()
        print "reservation", reservations
        for reservation in  reservations:
            print "instance:", reservation.instances[0].id


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
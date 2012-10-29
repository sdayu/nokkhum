'''
Created on Jul 13, 2012

@author: boatkrap
'''
import unittest
from nokkhum import controller, models
import configparser
import os

from nokkhum.cloud.vm import ec2

class Test(unittest.TestCase):


    def setUp(self):
        config_file = "../../configuration.ini"
        config = configparser.ConfigParser()
        config.read(config_file)
        
        self.config = config
        
        controller.config = config
        setting = dict()
        for k, v in config.items("controller"):
            setting[k] = v
        
        models.initial(setting) 
        
        log_path = setting["nokkhum.log_dir"]
        if not os.path.exists(log_path):
            os.mkdir(log_path)
        
        import logging.config
        logging.config.fileConfig(config_file)
        access_key_id       = config.get('controller', "nokkhum.vm.ec2.access_key_id")
        secret_access_key   = config.get('controller', "nokkhum.vm.ec2.secret_access_key")
        host    = config.get('controller', "nokkhum.vm.ec2.host")
        port    = config.getint('controller', "nokkhum.vm.ec2.port")
        secure  = config.getboolean('controller', "nokkhum.vm.ec2.secure_connection")
#        region_name= setting["nokkhum.vm.ec2.region_name"]
#        path= setting["nokkhum.vm.ec2.path"]
        
        print ("host:", host)
        print ("port:", port)
        print ("secure:", secure)
        self.ec2 = ec2.EC2Client(access_key_id, secret_access_key, host, port, secure)


    def tearDown(self):
        pass
    
    def testGetImage(self):
        image_name = self.config.get('controller', "nokkhum.vm.ec2.image.name")
        print ("image name:", image_name)
        image = self.ec2.get_image(image_name)
        print ("image:",image.name)

    def testListImage(self):
        images = self.ec2.get_all_images()
        for image in images:
            print ('image:',image.name, "location:", image.location)
    
    def testListInstance(self):
        reservations = self.ec2.get_all_instances()
        print ("reservation", reservations)
        for reservation in  reservations:
            print ("instance:", reservation.instances[0].id)
            print ("instance dict:", reservation.instances[0].__dict__)
            print ("instance ip:", reservation.instances[0].private_ip_address)
            

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
'''
Created on Aug 3, 2012

@author: boatkrap
'''
import unittest
from nokkhum import controller, models
import ConfigParser
import os

from nokkhum.cloud.vm import ec2


class Test(unittest.TestCase):

    def setUp(self):
        config_file = "../../../controller-config.ini"
        config = ConfigParser.ConfigParser()
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
        access_key_id = config.get(
            'controller', "nokkhum.vm.ec2.access_key_id")
        secret_access_key = config.get(
            'controller', "nokkhum.vm.ec2.secret_access_key")
        host = config.get('controller', "nokkhum.vm.ec2.host")
        port = config.getint('controller', "nokkhum.vm.ec2.port")
        secure = config.getboolean(
            'controller', "nokkhum.vm.ec2.secure_connection")
#        region_name= setting["nokkhum.ec2.region_name"]
#        path= setting["nokkhum.ec2.path"]

        print("host:", host)
        print("port:", port)
        print("secure:", secure)
        self.ec2 = ec2.EC2Client(
            access_key_id, secret_access_key, host, port, secure)

    def testRunInstance(self):
        image_name = "cirros-0.3.0-x86_64"
        instance = self.ec2.start_instance(image_name)
        print("start %s success", image_name)
        import time
        time.sleep(60)

        self.ec2.terminate_instance(instance.id)
        print("stop %s success", instance.id)


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()

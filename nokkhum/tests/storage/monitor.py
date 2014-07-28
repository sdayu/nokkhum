'''
Created on Jul 9, 2012

@author: boatkrap
'''
import unittest
from nokkhum import controller, models
from nokkhum import config


class Test(unittest.TestCase):

    def setUp(self):
        config_file = "../../../controller-config.ini"

        configuration = config.Configurator(config_file)

        controller.config = configuration
        setting = dict()

        for k, v in configuration.items():
            setting[k] = v

        models.initial(setting)

        import os
        if not os.path.exists(setting.get("nokkhum.log_dir")):

            os.makedirs(setting.get("nokkhum.log_dir"))

        import logging.config
        logging.config.fileConfig(config_file)

    def tearDown(self):
        pass

    def testStorageMonitoring(self):
        from nokkhum.controller.storage import monitor
        storage_thread = monitor.StorageMonitoring()
        storage_thread.start()
        storage_thread.join()


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()

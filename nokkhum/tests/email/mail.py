'''
Created on Jan 28, 2013

@author: boatkrap
'''
import unittest
from nokkhum import controller, models, config
import configparser
import os


class Test(unittest.TestCase):

    def setUp(self):
        config_file = "../../configuration.ini"
        config.settings = config.Configurator(config_file)

        settings = config.settings
        models.initial(settings)

        log_path = settings.get("nokkhum.log_dir")
        if not os.path.exists(log_path):
            os.mkdir(log_path)

        import logging.config
        logging.config.fileConfig(config_file)

        self.camera_id = 2

    def tearDown(self):
        pass

    def test_send_mail(self):
        from nokkhum.controller.notification import EmailNotification
        email_noti = EmailNotification()
        email_noti.send_mail(self.camera_id)


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()

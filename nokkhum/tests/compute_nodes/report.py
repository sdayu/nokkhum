'''
Created on May 30, 2013

@author: boatkrap
'''
import unittest
import os
from nokkhum import config


class ReportTest(unittest.TestCase):

    def setUp(self):
        configuration = config.Configurator("../../compute-config.ini")
        if not os.path.exists(config.Configurator.settings["nokkhum.processor.record_path"]):
            os.mkdir(
                config.Configurator.settings["nokkhum.processor.record_path"])

    def tearDown(self):
        pass

    def test_system_report(self):
        from nokkhum.compute import update_infomation
        print("config: ", config.Configurator.settings)
        ui = update_infomation.UpdateInfomation(None)
        resource = ui.get_resource()
        print("result: ", resource)
        self.assertIn("disk", resource)
        self.assertIn("cpu", resource)
        self.assertIn("memory", resource)

        self.assertGreaterEqual(
            resource["cpu"]["used"], 0, "cpu use less than 0")
        self.assertGreaterEqual(
            resource["memory"]["used"], 0, "cpu use less than 0")
        self.assertGreaterEqual(
            resource["disk"]["used"], 0, "cpu use less than 0")

if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()

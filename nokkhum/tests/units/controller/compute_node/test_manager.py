'''
Created on Jul 29, 2014

@author: boatkrap
'''
import unittest

from nokkhum import models


class TestResourceUsageComputeNodeManager(unittest.TestCase):
    def setUp(self):
        settings = {
            'mongodb.host': 'localhost',
            'mongodb.db_name': 'nokkhum'
        }

        models.initial(settings)

    def tearDown(self):
        pass

    def test_get_available_compute_node(self):
        from nokkhum.controller.compute_node import manager
        cnm = manager.ResourceUsageComputeNodeManager()
        processor = models.Processor.objects().first()
        cnm.get_compute_node_available_resource(processor)

if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()

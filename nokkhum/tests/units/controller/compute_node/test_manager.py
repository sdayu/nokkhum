'''
Created on Jul 29, 2014

@author: boatkrap
'''
import unittest

from nokkhum import models


class TestManager(unittest.TestCase):

    def setUp(self):
        settings = {
            'mongodb.host': '172.30.235.254',
            'mongodb.db_name': 'nokkhum'
        }

        models.initial(settings)

    def tearDown(self):
        pass

    def test_get_available_compute_node(self):
        from nokkhum.controller.compute_node import manager
        cnm = manager.ComputeNodeManager()
        compute_nodes = models.ComputeNode.objects().all()
        for compute_node in compute_nodes:
            cnm.is_compute_node_available(compute_node)


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()

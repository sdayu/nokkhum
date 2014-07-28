'''
Created on Nov 7, 2011

@author: boatkrap
'''
import unittest
from nokkhum import controller, model
from nokkhum.controller.manager import compute_node


class NodeManagerTest(unittest.TestCase):

    def testNodeAvialable(self):
        config = ConfigParser.ConfigParser()
        config.read("../../configuration.ini")

        controller.config = config
        model.initial(config)

        nm = compute_node.ComputeNodeManager()

        compute_nodes = nm.getAvialableComputeNode()

        for node in compute_nodes:
            print("name: ", node.name, " update_date: ", node.update_date)


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']

    unittest.main()

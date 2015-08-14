'''
Created on Oct 3, 2014

@author: boatkrap
'''

import unittest
from nokkhum import config
import os
from nokkhum.compute.machine_specification import MachineSpecification


class TestMachineSpecification(unittest.TestCase):
    def setUp(self):
        configurator = config.Configurator('/home/boatkrap/nokkhum-projects/nokkhum/compute-config.ini')

        directory = configurator.settings.get('nokkhum.log_dir')
        if not os.path.exists(directory):
            os.makedirs(directory)

        record_directory = configurator.settings.get('nokkhum.processor.record_path')
        if not os.path.exists(record_directory):
            os.makedirs(record_directory)

    def tearDown(self):
        pass

    def test_get_specification(self):
        ms = MachineSpecification('/tmp')
        msinfo = ms.get_specification()
        self.assertNotEqual(msinfo['cpu_frequency'], 0)
        self.assertNotEqual(msinfo['cpu_model'], '')


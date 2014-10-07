'''
Created on Oct 3, 2014

@author: boatkrap
'''

import unittest
from nokkhum import config
import os


class TestBenchmark(unittest.TestCase):
    def setUp(self):
        configurator = config.Configurator('/home/boatkrap/VSaaS/nokkhum/compute-config.ini')

        directory = configurator.settings.get('nokkhum.log_dir')
        if not os.path.exists(directory):
            os.makedirs(directory)

        record_directory = configurator.settings.get('nokkhum.processor.record_path')
        if not os.path.exists(record_directory):
            os.makedirs(record_directory)

    def tearDown(self):
        pass

    def test_benchmark(self):
        from nokkhum.compute import benchmark
        bm = benchmark.BenchmarkManger()
        attributes = "{}"
        bm.benchmake(attributes)


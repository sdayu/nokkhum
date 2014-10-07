'''
Created on Oct 2, 2014

@author: boatkrap
'''

from .processors import processors


class BenchmarkManger:
    def __init__(self):
        self.processor = processors.ImageProcessor('processor')

    def benchmake(self, attributes):
        print(attributes)

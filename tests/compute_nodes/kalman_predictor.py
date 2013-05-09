'''
Created on Apr 26, 2013

@author: boatkrap
'''
import unittest
import datetime
from nokkhum import models, controller
from nokkhum import config

from nokkhum.controller.compute_node import resource_predictor

class KalmanPredictorTest(unittest.TestCase):


    def test_predictor(self):
        
        configuration = config.Configurator("../../controller-config.ini")
        
        models.initial(configuration.settings) 
        
        kp = resource_predictor.KalmanPredictor()
        
        cpu = []
        for compute_node in models.ComputeNode.objects().all():
            records = models.ComputeNodeReport.objects(compute_node=compute_node, 
                                                       report_date__gt=datetime.datetime.now() - datetime.timedelta(days=40))\
                                                        .order_by("-report_date").limit(20)
            #records = records.order_by("+report_date")
            print("len", len(records))
            cpu = [record.cpu.usage for record in records]
            
            if len(cpu) <= 0:
                continue
            
            cpu.reverse()
            
            ram = [record.memory.total for record in records]
            ram.reverse()
            
            print ("predict cpu compute id: ",compute_node.id, kp.predict(cpu))
            print ("predict ram compute id: ",compute_node.id, kp.predict(ram))
            


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
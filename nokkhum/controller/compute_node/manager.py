'''
Created on Nov 7, 2011

@author: boatkrap
'''
import datetime

from nokkhum import models

class ComputeNodeManager(object):
    '''
    classdocs
    '''


    def __init__(self):
        '''
        Constructor
        '''
        
    def describe_avialable_compute_node(self):
        compute_nodes = models.ComputeNode.objects().all()
        return compute_nodes;
    
    def get_avialable_compute_node(self):
        delta = datetime.timedelta(minutes=1)
        now = datetime.datetime.now()
                
        compute_nodes = models.ComputeNode.objects(update_date__gt=now-delta).all()
        
        return compute_nodes;
    
    def get_compute_node_available_resource(self):
        '''
        need appropriate scheduling about CPU and RAM
        '''
        compute_nodes = self.get_avialable_compute_node()
        
        for compute_node in compute_nodes:
            if compute_node.cpu.usage < 95\
            and compute_node.memory.free%1000000 > 1:
                return compute_node
            
        return None
    
    
        
        
'''
Created on Nov 7, 2011

@author: boatkrap
'''
import datetime

from nokkhum import models

import logging
logger = logging.getLogger(__name__)

class ComputeNodeManager(object):
    '''
    classdocs
    '''


    def __init__(self):
        '''
        Constructor
        '''
    def describe_compute_node(self):
        compute_nodes = models.ComputeNode.objects().all()
        return compute_nodes;
    
    def describe_available_compute_node(self):
        compute_nodes = models.ComputeNode.objects().all()
        return compute_nodes;
    
    def get_available_compute_node(self):
        delta = datetime.timedelta(minutes=1)
        now = datetime.datetime.now()
                
        compute_nodes = models.ComputeNode.objects(update_date__gt=now-delta).all()
        
        return compute_nodes;
    
    def get_compute_node_available_resource(self):
        '''
        need appropriate scheduling about CPU and RAM
        '''
        compute_nodes = self.get_available_compute_node()
        
        for compute_node in compute_nodes:
            if compute_node.is_available_resource():
                return compute_node
            
        return None
    
        
        
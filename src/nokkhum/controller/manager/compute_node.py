'''
Created on Nov 7, 2011

@author: boatkrap
'''
import datetime

from nokkhum import model

class ComputeNodeManager(object):
    '''
    classdocs
    '''


    def __init__(self):
        '''
        Constructor
        '''
        
    def describe_avialable_compute_node(self):
        compute_nodes = model.ComputeNode.objects().all()
        return compute_nodes;
    
    def get_avialable_compute_node(self):
        delta = datetime.timedelta(minutes=1)
        now = datetime.datetime.now()
                
        compute_nodes = model.ComputeNode.objects(update_date__gt=now-delta).all()
        
        return compute_nodes;
    
    def get_compute_node_avialable_resource(self):
        compute_nodes = self.get_avialable_compute_node()
    
    
        
        
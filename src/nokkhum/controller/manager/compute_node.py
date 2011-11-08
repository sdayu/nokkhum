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
        
    def describeAvialableComputeNode(self):
        compute_nodes = model.ComputeNode.objects().all()
        return compute_nodes;
    
    def getAvialableComputeNode(self):
        delta = datetime.timedelta(minutes=1)
        now = datetime.datetime.now()
                
        compute_nodes = model.ComputeNode.objects(update_date__gt=now-delta).all()
        
        return compute_nodes;
        
        
'''
Created on Nov 1, 2011

@author: boatkrap
'''

import subprocess

from twisted.web import resource
from twisted.python import log

import datetime

from nokkhum.util import PageNotFoundError
from nokkhum import model

import json

class ComputeNode(resource.Resource):
    def __init__(self):
        resource.Resource.__init__(self)
        self.views = {
                     'update_system' : UpdateComputeNode(),
                      'update_stat' : UpdateComputeNodeStatus()
                     }
        
        for viewName, className in self.views.items():
        #add the view to the web service
            self.putChild(viewName, className)


    def render_GET(self, request):
        '''
        get response method for the root resource
        '''
        return 'Welcome to the REST API for Camera'

    def getChild(self, name, request):
        '''
        We overrite the get child function so that we can handle invalid
        requests
        '''
        
        if name == '':
            return self
        else:
            
            if name in self.views.keys():
                return resource.Resource.getChild(self, name, request)
            else:
                return PageNotFoundError()
            
class UpdateComputeNode(resource.Resource):

    def render_POST(self, request):
        result = dict()
        try:
            name        = request.args['name'][0]
            port        = request.args['port'][0]
            cpu_count   = request.args['cpu_count'][0]
            total_ram   = request.args['total_ram'][0]
            system      = request.args['system'][0]
            machine     = request.args['machine'][0]
            host        = request.getRequestHostname()
            
            log.msg( 'Begin to update compute node name: ' + name)
            
            compute_node = model.ComputeNode.objects(name=name, host=host).first()
            if compute_node is None:
                compute_node = model.ComputeNode()
                compute_node.name = name
                compute_node.host = host
                
            cpu = model.CPUInfomation()
            cpu.count = cpu_count
            
            memory = model.MemoryInfomation()
            memory.total = total_ram
            
            compute_node.port    = port
            compute_node.machine = machine
            compute_node.system  = system
            compute_node.cpu     = cpu
            compute_node.memory  = memory
            compute_node.update_date = datetime.datetime.now()
            compute_node.save()
        
            result["result"] = "update ok"
            log.msg( 'Compute node name: "%s" update complete' % ( name ) )
        except:
            log.err()
            result["result"] = 'Update Compute Node Error'
        
        return json.dumps(result)
    
class UpdateComputeNodeStatus(resource.Resource):

    def render_POST(self, request):
        result = dict()
        try:
            name        = request.args['name'][0]
            cpu_str     = request.args['cpu'][0]
            memory_str  = request.args['memory'][0]
            host        = request.getRequestHostname()
            
            compute_node = model.ComputeNode.objects(name=name, host=host).first()
            if compute_node is None:
                result["result"] = "Compute node is unavailable"
                return json.dumps(result)
            
            cpu     = json.loads(cpu_str)
            memory  = json.loads(memory_str)
            
            compute_node.cpu.user   = cpu["user"]
            compute_node.cpu.nice   = cpu["nice"]
            compute_node.cpu.system = cpu["system"]
            compute_node.cpu.idle   = cpu["idle"]
            
            compute_node.memory.total = memory["total"]
            compute_node.memory.used  = memory["used"]
            compute_node.memory.free  = memory["free"]
            
            compute_node.update_date = datetime.datetime.now()
            compute_node.save()
        
            result["result"] = "update success"
            log.msg( 'Compute node name: "%s" update stat complete' % ( name ) )
        except:
            log.err()
            result["result"] = 'Update Compute Node Stat Error'
        
        return json.dumps(result)

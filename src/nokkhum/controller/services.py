'''
Created on Sep 8, 2011

@author: boatkrap
'''


import sys, json, os
from twisted.internet import reactor
from twisted.web import server, resource
from twisted.web.static import File
from twisted.python import log
from twisted.python.logfile import DailyLogFile
from datetime import datetime

from nokkhum.util import PageNotFoundError
from nokkhum.controller import compute_node
from nokkhum import controller

#main server resource
class Root(resource.Resource):
    
    def __init__(self):
        resource.Resource.__init__(self)
        
        self.views = {
                  'compute_node' : compute_node.ComputeNode()
                  }
        
        for viewName, className in self.views.items():
            self.putChild(viewName, className)
    
    def render_GET(self, request):
        '''
        get response method for the root resource
        localhost:9000/
        '''
        return 'Welcome to the REST API'
    
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
            
def start():
    root = Root()

    log.msg('Starting nokkhum controller server: %s' % str(datetime.now()))

    controller_server = server.Site(root)
    port_num = int(controller.config.get('controller', 'nokkhum.controller.port'))
    reactor.listenTCP(port_num, controller_server)
    reactor.run()

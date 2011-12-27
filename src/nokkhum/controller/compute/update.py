'''
Created on Dec 23, 2011

@author: boatkrap
'''

import threading

from nokkhum.common.messages import consumer
from twisted.python import log

class UpdateStatus(threading.Thread):
    
    def __init__(self):
        threading.Thread.__init__(self)
        self._consumer = consumer.ConsumerFactory().get_consumer("nokkhum_compute.update_status")
        self.connection = consumer.ConsumerFactory().get_connection()
        self.update()
        
    def update(self):
        def process_msg(body, message):
            print body
            message.ack()
        
        print "yes --- > update"
        self._consumer.register(process_msg)

        
    def run(self):

        while True:
            log.msg("run message - >")
            self.connection.drain_events()
            log.msg("run message")
        
    
    
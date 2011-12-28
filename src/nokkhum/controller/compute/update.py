'''
Created on Dec 23, 2011

@author: boatkrap
'''

import threading

from nokkhum.common.messages import consumer
import logging

logger = logging.getLogger(__name__)

class UpdateStatus(threading.Thread):
    
    def __init__(self):
        threading.Thread.__init__(self)
        self._consumer = consumer.ConsumerFactory().get_consumer("nokkhum_compute.update_status")
        self.connection = consumer.ConsumerFactory().get_connection()
        self.update()
        self._running = False
        
    def update(self):
        def process_msg(body, message):
            print body
            message.ack()
        
        self._consumer.register(process_msg)

        
    def run(self):

        self._running = True
        while self._running:
            self.connection.drain_events()

    
    
    
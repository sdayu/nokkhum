'''
Created on Dec 23, 2011

@author: boatkrap
'''

import kombu
from kombu.common import maybe_declare

from . import queues

import logging
logger = logging.getLogger(__name__)

class Publisher:
    def __init__(self, exchange_name, channel, routing_key=None):

        self.exchange_name = exchange_name
        self._producer = None
        
        self.exchange = None
        self.channel = channel
        self.routing_key_list = []
        self.routing_key = routing_key
        
        self.reconnect(channel)
        
        if self.routing_key:
            self.queue_declare(self.routing_key)
        
        
    def reconnect(self, channel):
        self.exchange = kombu.Exchange(self.exchange_name, type="direct", durable=True)
        self.channel = channel
        
        self._producer = kombu.Producer(exchange=self.exchange,
            channel=channel, serializer="json", 
            routing_key=self.routing_key)
    
    def queue_declare(self, routing_key):
        if routing_key is None:
            return
        
        if routing_key in self.routing_key_list:
            return
        
        self.routing_key_list.append(routing_key)
        
        queue = queues.QueueFactory().get_queue(self.exchange, routing_key)
        if queue:
            queue(self.channel).declare()
            
    def send(self, message, routing_key=None):
        self._producer.publish(message, routing_key=routing_key)
        
class TopicPublisher(Publisher):
    def __init__(self, exchange_name, channel, routing_key=None):
        super().__init__(exchange_name, channel, routing_key) 
        
    def reconnect(self, channel):
        self.exchange = kombu.Exchange(self.exchange_name, type="topic", durable=True)
        self.channel = channel
        self._producer = kombu.Producer(exchange=self.exchange,
            channel=channel, serializer="json", 
            routing_key=self.routing_key)
        
        
class PublisherFactory:
    def __init__(self, channel):
        self.channel = channel
    
    def get_publisher(self, key):
        
        publisher = None
        logger.debug("routing_key: %s"% key)
        if key == "nokkhum_compute.update_status":
            routing_key = "nokkhum_compute.update_status"

            publisher = Publisher("nokkunm_compute.update_status", self.channel, routing_key)
            # logger.debug("get pub: %s"% publisher)
            return publisher
        
        else:
            import fnmatch, re
            regex = fnmatch.translate('nokkhum_compute.*.rpc_*')
            reobj = re.compile(regex)
            if reobj.match(key):
                routing_key = key
                
                if "nokkhum_compute.*.rpc_response" in routing_key:
                    publisher = TopicPublisher("nokkunm_compute.compute_rpc", self.channel, routing_key)
                elif "nokkhum_compute.*.rpc_request":
                    publisher = TopicPublisher("nokkunm_compute.rpc", self.channel, routing_key)
                # logger.debug("get pub: %s"%publisher)
                return publisher
            
        return publisher
            
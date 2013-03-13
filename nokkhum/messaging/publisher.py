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
        self.routing_key = routing_key
        self.routing_key_list = []
        
        self.reconnect(channel)
        
        
    def reconnect(self, channel):
        self.exchange = kombu.Exchange(self.exchange_name, type="direct", durable=True, auto_delete=True)
        self.channel = channel
        
        self._producer = kombu.Producer(exchange=self.exchange,
            channel=channel, serializer="json", 
            routing_key=self.routing_key)
        
        self.queue_declare(self.routing_key)
            
    def queue_declare(self, routing_key):
        if routing_key is None:
            return
        
        if routing_key in self.routing_key_list:
            return
        
        self.routing_key_list.append(routing_key)
        
        queue = queues.QueueFactory().get_queue(self.exchange, routing_key)
        queue(self.channel).declare()
            
    def send(self, message, routing_key=None):
        self._producer.publish(message, routing_key=routing_key)
        
class TopicPublisher(Publisher):
    def __init__(self, exchange_name, channel, routing_key=None):
        super().__init__(exchange_name, channel, routing_key) 
        
    def reconnect(self, channel):
        self.exchange = kombu.Exchange(self.exchange_name, type="topic", durable=True, auto_delete=True)
        self.channel = channel
        
        self._producer = kombu.Producer(exchange=self.exchange,
            channel=channel, serializer="json", 
            routing_key=self.routing_key)
        
        
class PublisherFactory:
    def __init__(self, channel):
        self.channel = channel
    
    def get_publisher(self, exchange_name):
        
        publisher = None
        logger.debug("exchange_name: %s"% exchange_name)
        if exchange_name == "nokkhum_compute.update_status":
            routing_key = "nokkhum_compute.update_status"

            publisher = Publisher("nokkunm_compute.update_status", self.channel, routing_key)
            # logger.debug("get pub: %s"% publisher)
            return publisher
        
        else:
            publisher = TopicPublisher(exchange_name, self.channel)
            logger.debug("get pub: %s"%exchange_name)
            return publisher
            
        return publisher
            
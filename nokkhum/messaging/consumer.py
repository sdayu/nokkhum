'''
Created on Dec 23, 2011

@author: boatkrap
'''
import kombu

from . import queues

import logging
logger = logging.getLogger(__name__)
class Consumer:

    def __init__(self, exchange_name, channel, routing_key, callback=None):
        self.exchange_name = exchange_name
        self.callback = callback
        self.routing_key = routing_key
        self._consumer = None
        self.reconnect(channel)

    def reconnect(self, channel):
        exchange = kombu.Exchange(self.exchange_name, type="direct", durable=True, auto_delete=True)
        queue = queues.QueueFactory().get_queue(exchange, self.routing_key)
        queue(channel).declare()
        self._consumer = kombu.Consumer(channel, queue, callbacks=self.callback)
        self.consume()
    
    def register_callback(self, callback):
        self._consumer.register_callback(callback)
        self.callback = callback
        import logging
        logger = logging.getLogger(__name__)
    
    def consume(self):
        self._consumer.consume()
        
class TopicConsumer(Consumer):
    
    def __init__(self, exchange_name, channel, routing_key, callback=None):
        Consumer.__init__(self, exchange_name, channel, routing_key)
        
    def reconnect(self, channel):
        exchange = kombu.Exchange(self.exchange_name, type="topic", durable=True, auto_delete=True)
        queue = queues.QueueFactory().get_queue(exchange, self.routing_key)
        queue(channel).declare()
        self._consumer = kombu.Consumer(channel, queue, callbacks=self.callback)
        self.consume()

class ConsumerFactory:
    def __init__(self, channel):
        self.channel = channel
        
    def get_consumer(self, key):
            
        consumer = None
        logger.debug("routing_key: %s"% key)
        if key == "nokkhum_compute.update_status":
            routing_key = "nokkhum_compute.update_status"

            consumer = Consumer("nokkunm_compute", self.channel, routing_key)
            return consumer
        else:
            import fnmatch, re
            regex = fnmatch.translate('nokkhum_compute.*.rpc_*')
            reobj = re.compile(regex)
            if reobj.match(key):
                routing_key = key

                if "rpc_request" in routing_key:
                    consumer = TopicConsumer("nokkunm_compute.compute_rpc", self.channel, routing_key)
                else:
                    consumer = TopicConsumer("nokkunm_compute.rpc", self.channel, routing_key)
#                logger.debug("get pub: %s"%publisher)
                return consumer
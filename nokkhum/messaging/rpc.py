'''
Created on Jan 11, 2012

@author: boatkrap
'''

import kombu.utils

from . import publisher
from . import consumer
import datetime

import logging
logger = logging.getLogger(__name__)

import time

class RPC:
    def __init__(self, channel):
        self._publisher = None
        self._consumer = None
        self.channel = channel
        
        self.message_pool = {}
        
        self.initial()
        
        
    def initial(self):
        self._publisher = publisher.PublisherFactory(self.channel).get_publisher("nokkhum_compute.*.rpc_request")
        self._consumer = consumer.ConsumerFactory(self.channel).get_consumer("nokkhum_compute.127:0:0:1.rpc_response")
        self.regist_default_consumer_callback()
    
    def regist_default_consumer_callback(self):
        def process_message(body, message):
            message.ack()
            if 'message_id' in body:
                self.message_pool[body['message_id']] = body
            else:
                logger.debug('message ignore by RPC: %s'%body)
                
        self._consumer.register_callback(process_message)
                
    def call(self, message, routing_key, time_out=120):
        message_id = kombu.utils.uuid()
        message['message_id'] = message_id
        message['reply_to'] = self._consumer_rounting_key 
        
        self.send(message, routing_key)
        
        start_wait_time = datetime.datetime.now()
        while message_id not in self.message_pool.keys():
            time.sleep(0.1)
            diff_time = datetime.datetime.now() - start_wait_time
            if diff_time.total_seconds() > time_out:
                break
        
        if message_id in self.message_pool.keys():
            response = self.message_pool[message_id]
            del self.message_pool[message_id]
        else:
            raise Exception('RPC Time out: %d s'%time_out)
        return response
        
    def send(self, message, routing_key):
        if routing_key not in self._publisher.routing_key_list:
            self._publisher.queue_declare(routing_key)
            
        self._publisher.send(message, routing_key)
        
    def register_request_queue(self, host):
        routing_key = "nokkhum_compute.%s.rpc_request"%host.replace('.', ":")
        if self._publisher is not None:
            self._publisher.queue_declare(routing_key)
        
        logger.debug("initial RPC queue name: "+routing_key)
        
class RpcClient(RPC):
    def __init__(self, channel, ip):
        #self._publisher_rounting_key    = "nokkhum_compute.*.rpc_request"
        self._consumer_rounting_key     = "nokkhum_compute.%s.rpc_response"%ip.replace('.', ":")
        super().__init__(channel)
        
    def initial(self):
        self._publisher = publisher.PublisherFactory(self.channel).get_publisher("nokkunm_compute.rpc")
        self._consumer = consumer.ConsumerFactory(self.channel).get_consumer(self._consumer_rounting_key)
        self.regist_default_consumer_callback()
        logger.debug("initial RPC Client")
        
    
    
class RpcServer(RPC):
    def __init__(self, channel, ip):
        #self._publisher_rounting_key    = "nokkhum_compute.%s.rpc_response"%ip.replace('.', ":")
        self._consumer_rounting_key     = "nokkhum_compute.%s.rpc_request"%ip.replace('.', ":")
        
        super().__init__(channel)
        
    def initial(self):
        self._publisher = publisher.PublisherFactory(self.channel).get_publisher("nokkunm_compute.compute_rpc")
        self._consumer = consumer.ConsumerFactory(self.channel).get_consumer(self._consumer_rounting_key)
        
        logger.debug("initial RPC Server")
        
    def register_callback(self, callback):
        self._consumer.register_callback(callback)
        
    def reply(self, message, route_key):
        self._publisher.send(message, route_key)

class RpcFactory:
    def __init__(self, channel):
        self.channel = channel
        self.default_rpc_client = None
        self.default_rpc_server = None
        
    def get_default_rpc_client(self, ip="127.0.0.1"):
        if self.default_rpc_client is None:
            self.default_rpc_client = RpcClient(self.channel, ip)
        return self.default_rpc_client
    
    def get_default_rpc_server(self, ip="127.0.0.1"):
        if self.default_rpc_server is None:
            self.default_rpc_server = RpcServer(self.channel, ip)
        return self.default_rpc_server
    
        

    

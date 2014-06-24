from kombu import BrokerConnection

import logging
logger = logging.getLogger(__name__)

from . import rpc
from . import publisher
from . import consumer

import time

import threading
cc = threading.Condition()

class Connection:
    connection = None
    
    def __init__(self, url):
        self.url = url
        self.__connection = None
        self.__running = True
        self.channel = None
        self.sleep_time = 10
        self.reconnect(url)
        
    @staticmethod
    def get_instance():
        if Connection.connection is None:
            Connection.connection = Connection()
        return Connection.connection
        
    def __connect(self):
        self.__connection = BrokerConnection(self.url)
        self.channel = self.get_channel()
        
        self.rpc_factory = rpc.RpcFactory(self.channel)
        self.publisher_factory = publisher.PublisherFactory(self.channel)
        self.consumer_factory = consumer.ConsumerFactory(self.channel)
        
        self.__running = True
        Connection.connection = self

    def get_broker_connection(self):
        if self.__connection is None:
            self.reconnect(self.url)
            
        return self.__connection
    
    def get_channel(self):
        if self.channel is None:
            self.channel = self.get_new_channel()
        return self.channel
    
    def get_new_channel(self):
        if self.__connection is None:
            self.reconnect(self.url)
        return self.__connection.channel()
    
    def get_rpc_factory(self):
        return self.rpc_factory
    
    def reconnect(self, url=None):
        cc.acquire()
        if self.__connection is not None:
            self.release()
            
        if url is not None:
            self.url = url
            
        logger.debug("reconnect connection")
        attempt = 0
        while True:
            try:
                self.__connect()
                cc.release()
                return
            except Exception as e:
                logging.exception(e)
            
            logging.debug("retry again in %s s"%self.sleep_time)
            time.sleep(self.sleep_time)
        cc.release()
        
    def drain_events(self):
        self.__connection.drain_events()
    
    def release(self):
        Connection.connection = None
        self.__running = False
        self.__connection.release()
        self.__connection.close()
        self.channel = None
        self.__connection = None

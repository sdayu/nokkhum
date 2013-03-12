from kombu import BrokerConnection

#import logging
#logger = logging.getLogger(__name__)

from . import rpc
from . import publisher
from . import consumer

class Connection:
    def __init__(self, url):
        self.url = url
        self.__connection = None
        self.__running = True
        self.__create()
        
    def __create(self):
        self.__connection = BrokerConnection(self.url)
        
        self.channel = self.get_new_channel()
        
        self.rpc_factory = rpc.RpcFactory(self.channel)
        self.publisher_factory = publisher.PublisherFactory(self.channel)
        self.consumer_factory = consumer.ConsumerFactory(self.channel)
        self.__running = True
    
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
    
    def reconnect(self, url):
        if self.__connection is not None:
            self.release()
        
        self.url = url
        self.__create()
        
    def drain_events(self):
        self.__connection.drain_events()
            
    
    def release(self):
        self.__running = False
        self.__connection.release()
        self.__connection.close()
        self.__connection = None
        
default_connection = None

def initial(url):
    global default_connection
    default_connection = Connection(url)
    
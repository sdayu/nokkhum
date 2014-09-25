'''
Created on Dec 23, 2011

@author: boatkrap
'''
import kombu
import time

from . import queues

import logging
logger = logging.getLogger(__name__)


class Consumer:

    def __init__(self, exchange_name, channel, routing_key, callback=None):
        self.exchange_name = exchange_name
        self.callback = callback
        self.routing_key = routing_key
        self._consumer = None
        self.routing_key_list = []
        self.exchange = None
        self.channel = None
        self.reconnect(channel)

    def reconnect(self, channel):
        self.channel = channel
        self.exchange = kombu.Exchange(
            self.exchange_name, type="direct", durable=True)

        try:
            self.queue = self.queue_declare(self.routing_key)
            self._consumer = kombu.Consumer(
                channel, self.queue, callbacks=self.callback)
            self.consume()

        except Exception as e:
            logger.exception(e)

    def queue_declare(self, routing_key):
        if routing_key is None:
            return

        if routing_key in self.routing_key_list:
            return

        self.routing_key_list.append(routing_key)

        queue = queues.QueueFactory().get_queue(self.exchange, routing_key)
        if queue:
            queue(self.channel).declare()

        return queue

    def register_callback(self, callback):
        while self._consumer is None:
            logger.debug("wait consumer")
            time.sleep(1)

        self._consumer.register_callback(callback)
        self.callback = callback

    def consume(self):
        self._consumer.consume()


class TopicConsumer(Consumer):

    def __init__(self, exchange_name, channel, routing_key, callback=None):
        Consumer.__init__(self, exchange_name, channel, routing_key)

    def reconnect(self, channel):
        exchange = kombu.Exchange(
            self.exchange_name, type="topic", durable=True)
        queue = queues.QueueFactory().get_queue(exchange, self.routing_key)
        queue(channel).declare()
        self._consumer = kombu.Consumer(
            channel, queue, callbacks=self.callback)
        self.consume()


class ConsumerFactory:

    def __init__(self, channel):
        self.channel = channel

    def get_consumer(self, key):

        consumer = None
        logger.debug("routing_key: %s" % key)
        if key == "nokkhum_compute.update_status":
            routing_key = "nokkhum_compute.update_status"

            consumer = Consumer(
                "nokkunm_compute.compute_update", self.channel, routing_key)
            return consumer
        else:
            import fnmatch
            import re
            regex = fnmatch.translate('nokkhum_compute.*.rpc_*')
            reobj = re.compile(regex)
            if reobj.match(key):
                routing_key = key

                if "rpc_request" in routing_key:
                    consumer = TopicConsumer(
                        "nokkunm_compute.compute_rpc", self.channel, routing_key)
                else:
                    consumer = TopicConsumer(
                        "nokkunm_compute.rpc", self.channel, routing_key)
#                logger.debug("get pub: %s"%publisher)
                return consumer

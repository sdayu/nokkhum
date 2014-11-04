'''
Created on Jan 11, 2012

@author: boatkrap
'''

from ..messaging import connection

from nokkhum import config
from nokkhum.controller.compute_node import update
from nokkhum.controller import schedule
import netifaces

import logging
logger = logging.getLogger(__name__)


class ControllerServer:

    def __init__(self, configuration):
        self._running = False

        self.configuration = configuration
        self.update_status = update.UpdateStatus()
        self.reconnect_message_connection()
        self.timer = schedule.timer.Timer()

    def reconnect_message_connection(self):
        from nokkhum.messaging import connection

        if connection.Connection.get_instance() is None:
            connection.Connection(self.configuration.settings.get('amq.url'))
        else:
            connection.Connection.get_instance().reconnect()

        ip = "127.0.0.1"
        try:
            ip = netifaces.ifaddresses(config.Configurator.settings.get(
                'nokkhum.controller.interface')).setdefault(netifaces.AF_INET)[0]['addr']
        except Exception as e:
            logger.exception(e)
            ip = netifaces.ifaddresses('lo').setdefault(
                netifaces.AF_INET)[0]['addr']

        self.rpc_client = connection.Connection.get_instance()\
            .get_rpc_factory().get_default_rpc_client(ip)
        self.update_consumer = connection.Connection.get_instance()\
            .consumer_factory.get_consumer("nokkhum_compute.update_status")
        self.update_status.set_consumer(self.update_consumer)

    def start(self):
        self._running = True
        self.update_status.start()
        self.timer.start()
        while self._running:
            logger.debug("drain_event")
            try:
                connection.Connection.get_instance().drain_events()
            except KeyboardInterrupt as e:
                self.stop()
                raise e
            except Exception as e:
                logger.exception(e)
                logger.debug("reconnect message server")
                # connection.Connection.get_instance().reconnect()
                self.reconnect_message_connection()

    def stop(self):
        self._running = False

        self.update_status.stop()
        self.timer.stop()

        self.update_status.join()
        self.timer.join()

        try:
            connection.Connection.get_instance().release()
        except:
            pass

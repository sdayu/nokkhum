'''
Created on Dec 2, 2011

@author: boatkrap
'''


import threading
import datetime
import time

import logging
logger = logging.getLogger(__name__)

from .processor import ProcessorScheduling
from ..processor.monitor import ProcessorMonitoring
from ..storage.monitor import StorageMonitoring
from ..vm.monitor import VMMonitoring

from nokkhum import config


class Timer(threading.Thread):

    def __init__(self):
        threading.Thread.__init__(self)
        self.name = self.__class__.__name__
        self.daemon = True

        self.processor_sheduling = None
        self.processor_monitoring = None
        self.clear_storage = None
        self.vm_monitoring = None

        self.wakeup_every = 10

        self._running = False

    def __processor_scheduling(self):
        if self.processor_sheduling is not None:
            if not self.processor_sheduling.is_alive():
                self.processor_sheduling.join()
                self.processor_sheduling = None

        if self.processor_sheduling is None:
            self.processor_sheduling = ProcessorScheduling()
            self.processor_sheduling.start()

    def __processor_monitoring(self):
        if self.processor_monitoring is not None:
            if not self.processor_monitoring.is_alive():
                self.processor_monitoring.join()
                self.processor_monitoring = None

        if self.processor_monitoring is None:
            self.processor_monitoring = ProcessorMonitoring()
            self.processor_monitoring.start()

    def __vm_monitoring(self):
        if self.vm_monitoring is not None:
            if not self.vm_monitoring.is_alive():
                self.vm_monitoring.join()
                self.vm_monitoring = None

        if self.vm_monitoring is None:
            self.vm_monitoring = VMMonitoring()
            self.vm_monitoring.start()

    def __storage_monitoring(self):
        if self.clear_storage is not None:
            if not self.clear_storage.is_alive():
                self.clear_storage.join()
                self.clear_storage = None

        current_time = datetime.datetime.now()
        if current_time.hour == 1 \
                and (current_time.minute >= 30 or current_time.minute < 40)\
                and self.clear_storage is None:

            try:
                self.clear_storage = StorageMonitoring()
                self.clear_storage.start()
            except Exception as e:
                logger.exception("storage error: %s" % e)

    def __start_scheduling(self):

        if config.Configurator.settings.get('nokkhum.vm.enable'):
            self.__vm_monitoring()

        self.__processor_scheduling()
        self.__processor_monitoring()

        if config.Configurator.settings.get('nokkhum.storage.enable'):
            self.__storage_monitoring()

    def run(self):
        self._running = True
        time.sleep(10)

        while(self._running):
            start_time = datetime.datetime.now()

            # check thread is alive
            logger.debug("Timer Thread Weakup")

            try:
                self.__start_scheduling()
            except Exception as e:
                logger.exception(e)

            end_time = datetime.datetime.now()

            delta = start_time - end_time
            sleep_time = self.wakeup_every - int(delta.total_seconds())

            if sleep_time > 0:
                logger.debug("Timer sleep %d " % sleep_time)
                time.sleep(sleep_time)

        logger.debug("Timer Exit Loop")

    def stop(self):
        self._running = False
        logger.debug("Timer Thread Stop")

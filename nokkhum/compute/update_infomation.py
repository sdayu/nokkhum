'''
Created on Nov 2, 2011

@author: boatkrap
'''

import platform
import json
import socket
import multiprocessing
import threading
import datetime
import time
import psutil
import netifaces
import fileinput

from . import s3

import logging
logger = logging.getLogger(__name__)

from nokkhum import config, compute
from . import machine_specification


class UpdateConfiguration:

    def update(self, settings):
        logger.debug("get variable: %s" % settings)
        for variable in settings.keys():
            config.Configurator.settings[variable] = settings[variable]


class UpdateInfomation:

    def __init__(self, publisher):

        self.publisher = publisher
        self.machine_specification = self.get_machine_specification()

        self.resource = self.get_resource()
        time.sleep(10)

    def set_publisher(self, publisher):
        self.publisher = publisher

    def send_message(self, messages):
        result = self.publisher.send(messages, "nokkhum_compute.update_status")
        logging.debug("result: %s send message: %s" % (result, messages))
        return result

    def get_machine_specification(self):
        ms = machine_specification.MachineSpecification(
            config.Configurator.settings.get('nokkhum.processor.record_path'),
            config.Configurator.settings.get('nokkhum.compute.interface')
        )

        result = ms.get_specification()
        return result

    def update_machine_specification(self):

        arguments = self.get_machine_specification()
        messages = {"method": "update_machine_specification", "args": arguments}
        logging.debug("update information: %s" % messages)

        return self.send_message(messages)

    def get_resource(self):

        cpus = psutil.cpu_percent(interval=.3, percpu=True)

        ms = self.machine_specification
        ip = ms['ip']

        cpu_prop = {
            "used": round(sum(cpus) / len(cpus)),
            "percpu": cpus,
        }

        mem = psutil.virtual_memory()
        mem_prop = {
            "total": mem.total,
            "used": mem.used,
            "free": mem.free
        }

        disk = psutil.disk_usage(
            config.Configurator.settings["nokkhum.processor.record_path"])
        disk_prop = {
            "total": disk.total,
            "used": disk.used,
            "free": disk.free,
            "percent": disk.percent,
        }

        processor_manager = compute.processor_manager
        processor_list = []

        pcpu = 0
        pmem = 0
        for pid, processor_id in processor_manager.get_pids():
            process = psutil.Process(pid)
            process_status = {
                'pid': pid,
                'processor_id': processor_id,
                'num_threads': process.num_threads(),
                'cpu': process.cpu_percent(interval=0.2),
                'memory': process.memory_info().rss,
                'messages': compute.processor_manager.read_process_output(processor_id)
            }
            pcpu += process_status['cpu']
            pmem += process_status['memory']

            processor_list.append(process_status)

        system_load={
            'cpu': sum(cpus)-pcpu if sum(cpus)-pcpu >= 0 else 0,
            'memory': mem.used-pmem if mem.used-pmem >= 0 else 0
        }

        resource = {
            'name': platform.node(),
            'cpu': cpu_prop,
            'memory': mem_prop,
            'disk': disk_prop,
            'processors': processor_list,
            'system_load': system_load,
            'ip': ip,
            'date': datetime.datetime.now().isoformat()
        }

        # logging.debug("update resource: %s" % messages)

        return resource

    def update_machine_resources(self):
        arguments = self.get_resource()
        self.resource = arguments
        messages = {"method": "update_machine_resources", "args": arguments}
        return self.send_message(messages)

    def get_processor_run_fail(self):
        processor_manager = compute.processor_manager
        dead_process = processor_manager.remove_dead_process()
        if len(dead_process) == 0:
            return None

        fail_processors = {
            'name': platform.node(),
            'ip': self.machine_specification['ip'],
            'dead_process': dead_process,
            'report_time': datetime.datetime.now().isoformat()
        }

#        logging.debug("camera_running_fail_report: %s" % messages)
        return fail_processors

    def processor_running_fail_report(self):
        arguments = self.get_processor_run_fail()
        if arguments is None:
            return
        messages = {"method": "processor_run_fail_report", "args": arguments}
        return self.send_message(messages)

    def check_resources(self):
        resource = self.get_resource()

        old_cpu = self.resource['cpu']['used']
        current_cpu = resource['cpu']['used']

        if abs(old_cpu - current_cpu) > 20:
            self.resource = resource
            messages = {"method": "update_machine_resources", "args": resource}
            return self.send_message(messages)

        self.processor_running_fail_report()


class UpdateStatus(threading.Thread):

    def __init__(self, publisher=None):
        threading.Thread.__init__(self)
        self.name = self.__class__.__name__
        self._running = False
        self.daemon = True
        self._request_sysinfo = False
        self.__s3thread = None

        self.publisher = publisher
        self.uinfo = UpdateInfomation(self.publisher)

    def set_publisher(self, publisher):
        self.publisher = publisher
        self.uinfo.set_publisher(self.publisher)

    def run(self):
        time_to_sleep = 2
        time_to_sent = 10

        counter = 0
        counter_sent = time_to_sent // time_to_sleep

        update_status = False

        self._running = True

        logger.debug("start update")

        while(self._running):
            while not update_status:
                update_status = self.uinfo.update_machine_specification()
                if not update_status:
                    logger.debug("wait message server %d second" %
                                 time_to_sleep)
                    time.sleep(time_to_sleep)

            while(self._running):
                # logger.debug("request_sysinfo %s"%self._request_sysinfo)
                if self._request_sysinfo:
                    self._request_sysinfo = False
                    update_status = False
                    # logger.debug("request_sysinfo -> break")
                    break

                start_time = datetime.datetime.now()
                if counter == counter_sent:
                    counter = 0
                    try:
                        self.uinfo.processor_running_fail_report()
                    except Exception as e:
                        logger.exception(e)

                    try:
                        self.uinfo.update_machine_resources()
                    except Exception as e:
                        logger.exception(e)

                    # sync to s3 storage
                    if config.Configurator.settings.get('nokkhum.storage.enable'):
                        if config.Configurator.settings.get('nokkhum.storage.api') == "s3":
                            self.push_s3 = True
                        else:
                            self.push_s3 = False
                    else:
                        self.uinfo.update_machine_specification()
                        self.push_s3 = False

                    if self.push_s3:
                        if self.__s3thread is not None and not self.__s3thread.is_alive():
                            self.__s3thread.join()
                            self.__s3thread = None

                        if self.__s3thread is None:
                            self.__s3thread = s3.S3Thread()
                            self.__s3thread.start()
                else:
                    try:
                        self.uinfo.check_resources()
                    except Exception as e:
                        logger.exception(e)

                end_time = datetime.datetime.now()

                delta = end_time - start_time
                sleep_time = time_to_sleep - delta.total_seconds()
                counter += 1
                if sleep_time > 0:
                    time.sleep(sleep_time)

        logger.debug(self.name + " terminate")

    def stop(self):
        self._running = False

    def get_machine_specification(self):
        self._request_sysinfo = True
        logger.debug("request_sysinfo: %s\n" % self._request_sysinfo)


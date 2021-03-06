'''
Created on Dec 23, 2011

@author: boatkrap
'''

import threading
import datetime
import time
import json

from nokkhum.messaging import connection
import logging

from nokkhum import models
from nokkhum import config


logger = logging.getLogger(__name__)


class ComputeNodeResource:

    def initial_central_configuration(self, host):
        storage_settings = {}

        for setting in config.Configurator.settings.keys():
            if 'nokkhum.storage' in setting:
                storage_settings[
                    setting] = config.Configurator.settings.get(setting)

        routing_key = "nokkhum_compute." + \
            host.replace('.', ':') + ".rpc_request"
        message = {"method": "update_system_configuration"}

        message['args'] = dict(settings=storage_settings)

        logger.debug('update storage to : "%s" message: %s routing_key: %s' % (
            host, message, routing_key))
        rpc_client = connection.Connection.get_instance(
        ).get_rpc_factory().get_default_rpc_client()
        rpc_client.send(message, routing_key)

    def update_machine_specification(self, args):

        try:
            name = args['name']
            cpu_count = args['cpu_count']
            cpu_model = args['cpu_model']
            cpu_frequency = args['cpu_frequency']
            total_memory = args['total_memory']
            total_disk = args['total_disk']
            system = args['system']
            machine = args['machine']
            host = args['ip']

            compute_node = models.ComputeNode.objects(host=host).first()

            if compute_node is None:
                compute_node = models.ComputeNode()
                compute_node.create_date = datetime.datetime.now()
                compute_node.host = host

            machine_specification = models.MachineSpecification()
            machine_specification.cpu_model = cpu_model
            machine_specification.cpu_count = cpu_count
            machine_specification.cpu_frequency = cpu_frequency
            machine_specification.total_memory = total_memory
            machine_specification.total_disk = total_disk
            machine_specification.machine = machine
            machine_specification.system = system

            compute_node.name = name
            compute_node.machine_specification = machine_specification
            compute_node.updated_date = datetime.datetime.now()
            compute_node.updated_resource_date = datetime.datetime.now()
            compute_node.push_responsed_date()
            compute_node.save()
            compute_node.reload()

            logger.debug(
                'Compute node name: "%s" update system info complete' % (name))

            rpc_client = connection.Connection.get_instance(
            ).get_rpc_factory().default_rpc_client
            if rpc_client is not None:
                routing_key = "nokkhum_compute.%s.rpc_request" % compute_node.host.replace(
                    ".", ":")
                rpc_client._publisher.drop_routing_key(routing_key)
        except Exception as e:
            logger.exception(e)

    def update_machine_resources(self, args):
        try:
            name = args['name']
            cpu = args['cpu']
            memory = args['memory']
            disk = args['disk']
            system_load = args['system_load']
            processors = args['processors']
            host = args['ip']
            reported_date = datetime.datetime.strptime(
                args['date'], '%Y-%m-%dT%H:%M:%S.%f')

            compute_node = models.ComputeNode.objects(host=host).first()

            if compute_node is None \
                    or datetime.datetime.now() - compute_node.updated_date > datetime.timedelta(seconds=30):

                routing_key = "nokkhum_compute." + \
                    host.replace('.', ':') + ".rpc_request"
                message = {"method": "get_machine_specification"}

                rpc_client = connection.Connection.get_instance()\
                    .get_rpc_factory().get_default_rpc_client()
                rpc_client.send(message, routing_key)
                logger.debug('compute node: "%s" unavailable. push %s by routing key: %s' % (
                    name, message, routing_key))

                if compute_node is None:
                    logger.debug('compute_node: is None')
                    return

            resource_usage = models.ResourceUsage()

            resource_usage.cpu.used = cpu["used"]
            resource_usage.cpu.used_per_cpu = cpu["percpu"]

            resource_usage.memory.total = memory["total"]
            resource_usage.memory.used = memory["used"]
            resource_usage.memory.free = memory["free"]

            resource_usage.disk.total = disk['total']
            resource_usage.disk.used = disk['used']
            resource_usage.disk.free = disk['free']
            resource_usage.disk.percent = disk['percent']

            resource_usage.system_load.cpu = system_load['cpu']
            resource_usage.system_load.memory = system_load['memory']

            resource_usage.reported_date = reported_date

            report = models.ComputeNodeReport()
            report.compute_node = compute_node
            report.reported_date = reported_date
            report.cpu = resource_usage.cpu
            report.memory = resource_usage.memory
            report.disk = resource_usage.disk
            report.system_load = resource_usage.system_load
            report.save()

            current_time = datetime.datetime.now()
            compute_node.push_resource(resource_usage)
            compute_node.updated_date = current_time
            compute_node.updated_resource_date = reported_date

            resource_usage.report = report
            compute_node.save()
            compute_node.reload()

            for processor_process in processors:
                processor = models.Processor.objects().with_id(
                    processor_process['processor_id'])
                processor.operating.status = "running"
                processor.operating.updated_date = current_time
                processor.operating.compute_node = compute_node
                processor.save()

                ps = models.ProcessorStatus()
                ps.processor = processor
                ps.reported_date = reported_date
                ps.cpu = processor_process['cpu']
                ps.memory = processor_process['memory']
                ps.threads = processor_process['num_threads']
                ps.messages = processor_process['messages']
                ps.compute_node_report = report
                ps.save()

                report.processor_status.append(ps)

                for message in processor_process['messages']:
                    try:
                        processor_message = json.loads(message)
                        if 'method' in processor_message:

                            if processor_message["method"] == "notify":

                                logger.debug("get notification")
                                from nokkhum.controller import notification
                                try:
                                    email = notification.EmailNotification()
                                    email.send_mail(processor.id)
                                except Exception as e:
                                    logger.exception(e)

                            if processor_message["method"] == "face_detected":
                                tmp = models.Notification()
                                tmp.method = processor_message["method"]
                                tmp.camera = processor_message["camera_id"]
                                tmp.description = processor_message[
                                    "description"]
                                tmp.filename = processor_message["filename"]
                                tmp.face_name = processor_message["face_name"]
                                tmp.save()

                            if processor_message["method"] == "motion_detected":
                                tmp = models.Notification()
                                tmp.method = processor_message["method"]
                                tmp.camera = processor_message["camera_id"]
                                tmp.description = processor_message[
                                    "description"]
                                tmp.face_name = processor_message["area"]
                                tmp.filename = ""
                                tmp.save()

                    except:
                        logger.exception("fail load json: %s" % message)

            report.save()

            logger.debug(
                'Compute node name: "%s" ip: %s update resource complete'
                % (name, host))
        except Exception as e:
            logger.exception(e)

    def processor_run_fail_report(self, args):
        try:
            name = args['name']
            host = args['ip']
            dead_process = args['dead_process']
            report_time = datetime.datetime.strptime(
                args['report_time'], '%Y-%m-%dT%H:%M:%S.%f')
            compute_node = models.ComputeNode.objects(
                name=name, host=host).first()
        except Exception as e:
            logger.exception(e)
            return

        logger.debug("controller get processor fail: %s" % args)

        for processor_id, message in dead_process.items():
            processor = models.Processor.objects().with_id(processor_id)
            if not processor:
                return

            processor_status = models.ProcessorRunFail()
            processor_status.processor = processor
            processor_status.compute_node = compute_node
            processor_status.message = message
            processor_status.report_time = report_time
            processor_status.process_time = datetime.datetime.now()
            processor_status.save()

            processor.operating.status = "fail"
            processor.operating.updated_date = datetime.datetime.now()
            processor.save()

            logger.debug('Compute node name: "%s" ip: %s got processor error id: %s msg:\n %s' % (
                name, host, processor_id, message))


class UpdateStatus(threading.Thread):

    def __init__(self, consumer=None):
        threading.Thread.__init__(self)
        self.name = self.__class__.__name__
        self.daemon = True
        self._running = False
        self._consumer = consumer
        self._cn_resource = ComputeNodeResource()

    def set_consumer(self, consumer):
        self._consumer = consumer
        self._consumer.register_callback(self.process_msg)

    def process_msg(self, body, message):
        if "method" not in body:
            logger.debug("ignore message", body)
            message.ack()
            return
        try:
            self.process_data(body)
        except Exception as e:
            logger.exception(e)

        message.ack()

    def process_data(self, body):
        # logger.debug("controller get message: %s" % body)
        if body["method"] == "update_machine_specification":
            self._cn_resource.update_machine_specification(body["args"])
            self._cn_resource.initial_central_configuration(body["args"]['ip'])
        elif body["method"] == "update_machine_resources":
            self._cn_resource.update_machine_resources(body["args"])
        elif body["method"] == "processor_run_fail_report":
            self._cn_resource.processor_run_fail_report(body["args"])

    def run(self):
        self._running = True
        while self._running:
            #            now = datetime.datetime.now()
            #            if now.minute == 0 and (now.second >= 0 and now.second <= 13):
            #                compute_nodes = models.ComputeNode.objects(updated_date__gt=now-datetime.timedelta(minutes=10)).all()
            #                for compute_node in compute_nodes:
            #                    self._cn_resource.initial_central_configuration(compute_node.host)

            time.sleep(10)

    def stop(self):
        self._running = False

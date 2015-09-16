'''
Created on Aug 23, 2012

@author: boatkrap
'''
from ..compute_node.manager import ComputeNodeManager, ResourceUsageComputeNodeManager
from .manager import VMManager
from nokkhum import models

from nokkhum.controller.compute_node.resource_predictor import KalmanPredictor

import threading
import logging
import datetime
logger = logging.getLogger(__name__)


class VMMonitoring(threading.Thread):

    def __init__(self):
        threading.Thread.__init__(self)
        self.name = 'VM Monitoring'
        self.daemon = True
        # self.compute_node_manager = ComputeNodeManager()
        self.compute_node_manager = ResourceUsageComputeNodeManager()

        self.vm_manager = VMManager()

    def run(self):
        logger.debug('VM Monitoring working')
        self.__monitor()
        logger.debug('VM Monitoring finish')

    def __manage(self):
        ''''''
        logger.debug('VM Monitoring check for terminate or reboot')
        compute_nodes = self.vm_manager.list_vm_compute_node()
        for compute_node in compute_nodes:
            if compute_node.is_online():

                if datetime.datetime.now() - compute_node.vm.started_instance_date \
                        < datetime.timedelta(minutes=30):
                    logger.debug('VM Monitoring compute node id %s instance id %s begin started' % (
                        compute_node.id, compute_node.vm.instance_id))
                    continue

                current_resource = compute_node.get_current_resources()
                if current_resource and current_resource.cpu.used > 5:
                    logger.debug('VM Monitoring compute node id %s instance id %s got CPU usage more than 5%%' % (
                        compute_node.id, compute_node.vm.instance_id))
                    continue

                logger.debug('VM Monitoring check compute node id %s instance id %s'
                             % (compute_node.id, compute_node.vm.instance_id))
#                 records = models.ComputeNodeReport.objects(
#                     compute_node=compute_node,
#                     reported_date__gt=datetime.datetime.now() - datetime.timedelta(minutes=2))\
#                         .order_by('-reported_date').limit(20)

                compute_node.reload()
                records = compute_node.resource_records[-20:]

                has_processor = False
                for record in records:
                    if len(record.report.processor_status) > 0:
                        has_processor = True
                        logger.debug('VM Monitoring predict compute node id %s instance id %s has processors' % (
                            compute_node.id, compute_node.vm.instance_id))
                        break

                if has_processor:
                    continue

                cpu = [record.cpu.used for record in records]
                cpu.reverse()
                kp = KalmanPredictor()
                cpu_predict = kp.predict(cpu)

                if cpu_predict < 5:
                    logger.debug('VM Monitoring terminate compute node id %s instance id %s' % (
                        compute_node.id, compute_node.vm.instance_id))
                    self.vm_manager.terminate(compute_node.vm.instance_id)

                    message = dict(
                        created_date=datetime.datetime.now(),
                        message='VM Monitoring terminate compute node free')

                    if 'message' not in compute_node.vm.extra:
                        compute_node.vm.extra['messages'] = []
                    compute_node.vm.extra['messages'].append(message)
                    compute_node.save()
            else:
                logger.debug(
                    'VM Monitoring check for reboot compute node id %s instance id %s'
                    % (compute_node.id, compute_node.vm.instance_id))
                ec2_instance = self.vm_manager.get(compute_node.vm.instance_id)
                if ec2_instance and ec2_instance.state != 'terminate':
                    if 'responsed_date' in compute_node.extra:
                        if ec2_instance.state == 'running' \
                                and compute_node.updated_date > datetime.datetime.now() - datetime.timedelta(minutes=15):
                            continue

                        logger.debug('VM Monitoring reboot compute node id %s instance id %s'
                                     % (compute_node.id,
                                        compute_node.vm.instance_id))
                        compute_node.updated_date = datetime.datetime.now()
                        message = dict(created_date=datetime.datetime.now(),
                                       message='VM Monitoring reboot',
                                       status=ec2_instance.update())
                        if 'message' not in compute_node.vm.extra:
                            compute_node.vm.extra['messages'] = []
                        compute_node.vm.extra['messages'].append(message)
                        compute_node.save()
                        self.vm_manager.reboot(compute_node.vm.instance_id)
                else:
                    logger.debug(
                        'VM Monitoring compute node id %s instance id %s already terminated'
                        % (compute_node.id, compute_node.vm.instance_id))
                    compute_node.status = 'terminate'

                    compute_node.updated_date = datetime.datetime.now()
                    message = dict(created_date=datetime.datetime.now(),
                                   message='VM Monitoring terminate')

                    if ec2_instance:
                        compute_node.vm.status = ec2_instance.update()
                        message['status'] = compute_node.vm.status
                    else:
                        compute_node.vm.status = 'terminate'
                        message['status'] = 'terminate with ec2 instance is None'

                    if 'message' not in compute_node.vm.extra:
                        compute_node.vm.extra['messages'] = []
                    compute_node.vm.extra['messages'].append(message)
                    compute_node.save()

    def __acquire(self):
        logger.debug('VM Monitoring check for acquisition')
        processor_command = models.ProcessorCommand.objects(
            action__iexact='start', status__iexact='waiting').first()

        if models.ProcessorCommandQueue.objects(
                processor_command=processor_command).first() is None:
            return

        if self.compute_node_manager.find_suitable_compute_node(
                processor_command.processor) is not None:
            return

        logger.debug('VM There are no available resource')
        compute_nodes = self.vm_manager.list_vm_compute_node()

        for compute_node in compute_nodes:
            if datetime.datetime.now() - compute_node.vm.started_instance_date < datetime.timedelta(minutes=20):
                if compute_node.vm.status == 'pending':
                    logger.debug('VM compute node id: %s instance id: %s in wait list' % (
                        compute_node.id, compute_node.vm.instance_id))
                    return
                elif 'responsed_date' not in compute_node.extra \
                        and datetime.datetime.now() - compute_node.vm.started_instance_date < datetime.timedelta(minutes=30):
                    logger.debug('VM compute node id: %s instance id: %s in wait for first time response in 30 minutes' % (
                        compute_node.id, compute_node.vm.instance_id))
                    return
                elif 'responsed_date' in compute_node.extra:
                    if datetime.datetime.now() - compute_node.extra['responsed_date'][-1] < datetime.timedelta(seconds=120):
                        logger.debug('VM compute node id: %s instance id: %s in wait for stable report resource in 60 seconds' % (
                            compute_node.id, compute_node.vm.instance_id))
                        return

        logger.debug('VM --> get vm')
        self.vm_manager.acquire()

    def __monitor(self):
        ''''''
        self.__manage()
        self.__acquire()

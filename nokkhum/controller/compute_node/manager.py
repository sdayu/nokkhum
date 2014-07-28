'''
Created on Nov 7, 2011

@author: boatkrap
'''
import datetime

from nokkhum import models

import logging
logger = logging.getLogger(__name__)

from .resource_predictor import KalmanPredictor


class ComputeNodeManager(object):

    '''
    classdocs
    '''

    def __init__(self):
        '''
        Constructor
        '''

    def describe_compute_node(self):
        compute_nodes = models.ComputeNode.objects().all()
        return compute_nodes

    def describe_available_compute_node(self):
        compute_nodes = models.ComputeNode.objects().all()
        return compute_nodes

    def get_available_compute_node(self):
        delta = datetime.timedelta(minutes=1)
        now = datetime.datetime.now()

        compute_nodes = models.ComputeNode.objects(
            updated_date__gt=now - delta).all()

        return compute_nodes

    def get_compute_node_available_resource(self):
        '''
        need appropriate scheduling about CPU and RAM
        '''
        compute_nodes = self.get_available_compute_node()

        for compute_node in compute_nodes:
            if self.is_compute_node_available(compute_node):
                return compute_node

        return None

    def is_compute_node_available(self, compute_node):

        records = models.ComputeNodeReport.objects(compute_node=compute_node,
                                                   reported_date__gt=datetime.datetime.now() - datetime.timedelta(minutes=1))\
            .order_by("-reported_date").limit(20)

        cpu = [record.cpu.used for record in records]
        ram = [record.memory.free for record in records]
        disk = [record.disk.free for record in records]

        if len(cpu) <= 0:
            return False

        cpu.reverse()
        ram.reverse()
        disk.reverse()

        kp = KalmanPredictor()
        cpu_predict = kp.predict(cpu)
        kp = KalmanPredictor()
        ram_predict = kp.predict(ram)
        kp = KalmanPredictor()
        disk_predict = kp.predict(disk)

        logger.debug(
            "compute node id: %s current/predict cpu: %s/%s ram: %s/%s disk: %s/%s" % (compute_node.id,
                                                                                       cpu[-
                                                                                           1], cpu_predict,
                                                                                       ram[-
                                                                                           1], ram_predict,
                                                                                       disk[-1], disk_predict))

        if cpu_predict < 70\
                and ram_predict / 1000000 > 200\
                and disk_predict / 1000000 > 1000:
            logger.debug("compute node id cpu: %s ram: %s disk %s" % (
                cpu_predict, ram_predict % 1000000, disk_predict % 1000000))
            return True

        # if compute node is not available
        return False

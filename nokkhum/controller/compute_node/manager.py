'''
Created on Nov 7, 2011

@author: boatkrap
'''
import datetime

from nokkhum import models
from .resource_predictor import KalmanPredictor


import logging
logger = logging.getLogger(__name__)


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

        records = compute_node.resource_records

        cpu = []
        ram = []
        disk = []
        last = datetime.datetime.now()-datetime.timedelta(minutes=2)
        for record in records:
            if record.reported_date > last:
                cpu.append(record.cpu.used)
                ram.append(record.memory.free)
                disk.append(record.disk.free)

        if len(cpu) <= 0:
            return False

        kp = KalmanPredictor()
        cpu_predict = kp.predict(cpu)
        kp = KalmanPredictor()
        ram_predict = kp.predict(ram)
        kp = KalmanPredictor()
        disk_predict = kp.predict(disk)

        logger.debug(
            "compute node id: %s current/predict cpu: %s/%s ram: %s/%s disk: %s/%s"
            % (compute_node.id,
               cpu[-1], cpu_predict,
               ram[-1], ram_predict,
               disk[-1], disk_predict)
            )

        # decision cpu prediction 70% CPU usage

        if cpu_predict < 70\
                and ram_predict / 1000000 > 200\
                and disk_predict / 1000000 > 1000:
            logger.debug("compute node id cpu: %s ram: %s disk %s" % (
                cpu_predict, ram_predict % 1000000, disk_predict % 1000000))
            return True

        # if compute node is not available
        return False

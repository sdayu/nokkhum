'''
Created on Nov 7, 2011

@author: boatkrap
'''
import datetime

from nokkhum import models
from .resource_predictor import KalmanPredictor


import logging
from nokkhum.models import image_processors
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

    def get_available_compute_nodes(self):
        # delta = datetime.timedelta(minutes=1)
        delta = datetime.timedelta(days=1)
        now = datetime.datetime.now()

        compute_nodes = models.ComputeNode.objects(
            updated_date__gt=now - delta).all()

        return compute_nodes

    def get_compute_node_available_resource(self, processor=None):
        '''
        need appropriate scheduling about CPU and RAM
        '''
        compute_nodes = self.get_available_compute_nodes()

        for compute_node in compute_nodes:
            if self.is_compute_node_available(compute_node):
                return compute_node

        return None

    def is_compute_node_available(self, compute_node):

        if not hasattr(compute_node, "resource_records")\
                or len(compute_node.resource_records) == 0:
            return False

        cpu_predict, memory_predict, disk_predict\
            = self.resource_prediction(compute_node)

        # decision cpu prediction 70% CPU usage
        if cpu_predict < 90\
                and memory_predict / 1000000 > 200\
                and disk_predict / 1000000 > 1000:
            logger.debug("compute node id cpu: %s ram: %s disk %s" % (
                cpu_predict, memory_predict % 1000000, disk_predict % 1000000))
            return True

        # if compute node is not available
        return False

    def resource_prediction(self, compute_node):
        print("compute_node:", compute_node.__dict__)
        records = compute_node.resource_records

        cpu = []
        memory = []
        disk = []
        last = datetime.datetime.now()-datetime.timedelta(minutes=2)
        # last = datetime.datetime.now()-datetime.timedelta(days=1)
        for record in records:
            if record.reported_date > last:
                cpu.append(record.cpu.used)
                memory.append(record.memory.free)
                disk.append(record.disk.free)

        if len(cpu) <= 0:
            return False

        kp = KalmanPredictor()
        cpu_predict = kp.predict(cpu)
        kp = KalmanPredictor()
        memory_predict = kp.predict(memory)
        kp = KalmanPredictor()
        disk_predict = kp.predict(disk)

        logger.debug(
            "compute node id: %s current/predict cpu: %s/%s ram: %s/%s disk: %s/%s" % (
                compute_node.id,
                cpu[-1], cpu_predict,
                memory[-1], memory_predict,
                disk[-1], disk_predict)
            )
        print("pre:", cpu_predict, memory_predict, disk_predict)

        return cpu_predict, memory_predict, disk_predict


class ResourceUsageComputeNodeManager(ComputeNodeManager):

    def predict_resource(self, processor, image_processors=None):

        camera = processor.cameras[0]

        fps = camera.fps
        video_size = list(map(int, camera.image_size.split('x')))

        print("video size:", video_size)

        cpu_usage = 0
        memory_usage = 0

        if image_processors is None:
            image_processors = processor.image_processors

        for ip in image_processors:
            if 'width' in ip:
                video_size = [ip['width'], ip['height']]
            ipx = models.ImageProcessingExperiment.objects(
                    image_analysis=ip['name'],
                    video_size=video_size,
                    fps=fps
                    ).first()
            if ipx:
                cpu_usage += ipx.heuristic['max_cpu_used']
                memory_usage += ipx.heuristic['max_memory_used']
#                 print("cpu:", cpu_usage, "memory:", memory_usage)

            if 'image_processors' in ip:
                cpu_r, memory_r = self.predict_resource(processor,
                                                        ip['image_processors'])
                cpu_usage += cpu_r
                memory_usage += memory_r

        return cpu_usage, memory_usage

    def find_suitable_compute_node(self, processor):

        print(len(list(self.get_available_compute_nodes_resource())))
        for compute_node in self.get_available_compute_nodes_resource():
#             print("compute_node:", compute_node.name)
            return compute_node

    def get_available_compute_nodes_resource(self):
        compute_nodes = self.get_available_compute_nodes()
        for compute_node in compute_nodes:
            if self.is_compute_node_available(compute_node):
                yield compute_node

    def get_compute_node_available_resource(self, processor=None):
        '''
        need appropriate scheduling about CPU and RAM
        '''

        if processor is None:
            return super().get_compute_node_available_resource(processor)

        else:
            return self.find_suitable_compute_node(processor)


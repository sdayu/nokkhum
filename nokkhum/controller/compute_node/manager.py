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
        self.CPU_UPPER_BOUND = 99
        self.CPU_RESERVE = 10

    def get_compute_nodes(self):
        compute_nodes = models.ComputeNode.objects().all()
        return compute_nodes

    def get_online_compute_nodes(self):
        delta = datetime.timedelta(minutes=1)
        now = datetime.datetime.now()

        compute_nodes = models.ComputeNode.objects(
            updated_date__gt=now - delta).all()
        return compute_nodes

    def get_available_compute_nodes(self):

        return (compute_node for compute_node in self.get_online_compute_nodes()\
                    if self.is_available_compute_node(compute_node))

    def get_suitable_compute_nodes(self, processor=None):
        yield from self.get_available_compute_nodes()

    def find_suitable_compute_node(self, processor=None):
        '''
        need appropriate scheduling about CPU and RAM
        '''
        compute_nodes = self.get_suitable_compute_nodes()
        for compute_node in compute_nodes:
            return compute_node

        return None

    def is_available_cpu(self, percent_cpu_usage, cpu_count=1):
        '''print(percent_cpu_usage,":", cpu_count*self.CPU_UPPER_BOUND)
        if( percent_cpu_usage < cpu_count*self.CPU_UPPER_BOUND):
            return True
'''
        print(percent_cpu_usage,":", cpu_count*100 - self.CPU_RESERVE)
        if  percent_cpu_usage < (cpu_count*100 - self.CPU_RESERVE):
            return True

        return False

    def is_available_memory(self, memory_usage, full_memory):
        if full_memory - (memory_usage / 1000000) > 200:
            return True

        return False

    def is_available_disk(self, disk_usage, full_disk):
        if full_disk - (disk_usage / 1000000) > 1000:
            return True

        return False

    def is_available_compute_node(self, compute_node):

        if not hasattr(compute_node, "resource_records")\
                or len(compute_node.resource_records) == 0:
            return False

        cpu_predict, memory_predict, disk_predict\
            = self.predict_resource(compute_node)

        print("predict: cpu",cpu_predict," memory:", memory_predict, " disk:", disk_predict)

        if cpu_predict:
            cpu_available = self.is_available_cpu(cpu_predict, compute_node.machine_specification.cpu_count)
            memory_available = self.is_available_memory(memory_predict, compute_node.machine_specification.total_memory)
            disk_available = self.is_available_disk(disk_predict, compute_node.machine_specification.total_disk)

            logger.debug("compute node id cpu: %s/%s ram: %s/%s disk %s/%s" % (
                cpu_predict, cpu_available, memory_predict % 1000000, memory_available,
                disk_predict % 1000000, disk_available))
            print("compute node id cpu: %s/%s ram: %s/%s disk %s/%s" % (
                cpu_predict, cpu_available, memory_predict % 1000000, memory_available,
                disk_predict % 1000000, disk_available))
            if cpu_available and memory_available and disk_available:
                return True

        # if compute node is not available
        return False

    def predict_resource(self, compute_node):

        if not hasattr(compute_node, "resource_records")\
                or len(compute_node.resource_records) == 0:
            return None, None, None

        records = compute_node.resource_records

        cpu = []
        memory = []
        disk = []
        last = datetime.datetime.now()-datetime.timedelta(minutes=2)
        # last = datetime.datetime.now()-datetime.timedelta(days=1)
        for record in records:
            if record.reported_date > last:
                # cpu.append(record.cpu.used)
                cpu.append(sum(record.cpu.used_per_cpu))
                memory.append(record.memory.free)
                disk.append(record.disk.free)

        if len(cpu) <= 0:
            return None, None, None

        kp = KalmanPredictor()
        cpu_predict = kp.predict(cpu)
        kp = KalmanPredictor()
        memory_predict = kp.predict(memory)
        kp = KalmanPredictor()
        disk_predict = kp.predict(disk)

        logger.debug(
            "predict compute node id: %s current/predict cpu: %s/%s ram: %s/%s disk: %s/%s" % (
                compute_node.id,
                cpu[-1], cpu_predict,
                memory[-1], memory_predict,
                disk[-1], disk_predict)
            )
        # print("pre:", cpu_predict, memory_predict, disk_predict)

        return cpu_predict, memory_predict, disk_predict


class ResourceUsageComputeNodeManager(ComputeNodeManager):
    def __init__(self):
        super().__init__()

    def predict_processor_resource(self, compute_node, processor, image_processors=None):

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
                    machine_specification__cpu_model = compute_node.machine_specification.cpu_model,
                    machine_specification__cpu_frequency = compute_node.machine_specification.cpu_frequency,
                    machine_specification__cpu_count = compute_node.machine_specification.cpu_count,
                    image_analysis=ip['name'],
                    video_size=video_size,
                    fps=fps
                    ).first()

            if ipx:
                print("found")
                cpu_usage += ipx.heuristic['max_cpu_used']
                memory_usage += ipx.heuristic['max_memory_used']
#                 print("cpu:", cpu_usage, "memory:", memory_usage)

            if 'image_processors' in ip:
                cpu_r, memory_r = self.predict_processor_resource(compute_node,
                                                            processor,
                                                            ip['image_processors'])
                cpu_usage += cpu_r
                memory_usage += memory_r

        return cpu_usage, memory_usage


    def get_suitable_compute_nodes(self, processor=None):
        if processor is None:
            yield from super().get_suitable_compute_nodes()
            return

        compute_nodes = super().get_available_compute_nodes()

        for compute_node in compute_nodes:
            if self.is_suitable_running(compute_node, processor):
                yield compute_node

        return []

    def find_suitable_compute_node(self, processor=None):

        if processor is None:
            suitable_compute_node = super().find_suitable_compute_node()
            return suitable_compute_node

        for compute_node in self.get_suitable_compute_nodes(processor):
            if self.is_suitable_running(compute_node, processor):
                return compute_node

    def is_suitable_running(self, compute_node, processor):
        if not hasattr(compute_node, "resource_records"):
            return False

        cn_cpu_usage, cn_memory_usage, cn_disk_usage \
                = self.predict_resource(compute_node)
        if cn_cpu_usage is None:
            return False

        processor_cpu_usage, processor_memory_usage \
                = self.predict_processor_resource(compute_node, processor)
        print("p cpu: %s p memory: %s" % (processor_cpu_usage, processor_memory_usage))
        print("cn cpu: %s cn memory: %s cn disk: %s"%(cn_cpu_usage, cn_memory_usage, cn_disk_usage))


        # cpu_available = compute_node.machine_specification.cpu_count*100 - cn_cpu_usage
        # memory_available = compute_node.machine_specification.total_memory - cn_memory_usage
        # print("available cn cpu: %s cn memory: %s "%(cpu_available, memory_available))

        cn_cpu_future = cn_cpu_usage + processor_cpu_usage
        cn_memory_future = cn_memory_usage + processor_memory_usage

        print("suitable check: %s:%s"%(self.is_available_cpu(cn_cpu_future, compute_node.machine_specification.cpu_count),
                self.is_available_memory(cn_memory_future, compute_node.machine_specification.total_memory)))

        if self.is_available_cpu(cn_cpu_future,
                                 compute_node.machine_specification.cpu_count) \
                and self.is_available_memory(cn_memory_future,
                                            compute_node.machine_specification.total_memory):
            return True

        return False



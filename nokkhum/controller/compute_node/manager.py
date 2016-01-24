'''
Created on Nov 7, 2011

@author: boatkrap
'''
import datetime

from nokkhum import models
from nokkhum import config
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

    def get_predict_resource(self, resource):
        kp = KalmanPredictor()
        resource_predict =  kp.predict(resource)

        return resource_predict

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

        cpu_predict = self.get_predict_resource(cpu)
        memory_predict = self.get_predict_resource(memory)
        disk_predict = self.get_predict_resource(disk)

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

    def get_heuristic_resources(self, ip_experimental):
        ip_heuristic = {
                'avg': {'cpu':'avg_cpu', 'memory': 'avg_memory'},
                'avg_max': {'cpu':'avg_max_cpu', 'memory': 'avg_max_memory'},
                'max': {'cpu':'max_cpu', 'memory': 'max_memory'},
                'avg_min': {'cpu':'avg_min_cpu', 'memory': 'avg_min_memory'},
                'min': {'cpu':'min_cpu', 'memory': 'min_memory'}
            }

        settings = config.Configurator.settings
        resource_key = ip_heuristic[settings['nokkhum.scheduler.processor.heuristic']]
        return ip_experimental.heuristic[resource_key['cpu']], ip_experimental.heuristic[resource_key['memory']]

    def get_image_processing_experiment(self, compute_node, processor, ip):

        camera = processor.cameras[0]
        fps = camera.fps
        video_size = list(map(int, camera.image_size.split('x')))

        cpu_usage = 0
        memory_usage = 0

        print("video size:", video_size)
        ipx = models.ImageProcessingExperiment.objects(
                    machine_specification__cpu_model = compute_node.machine_specification.cpu_model,
                    machine_specification__cpu_frequency = compute_node.machine_specification.cpu_frequency,
                    machine_specification__cpu_count = compute_node.machine_specification.cpu_count,
                    image_analysis=ip['name'],
                    video_size=video_size,
                    fps=fps
                    ).first()

        if ipx is None:
            f_set = set()
            frequency_x = models.ImageProcessingExperiment.objects(
                    image_analysis=ip['name'],
                    video_size=video_size,
                    fps=fps
                    ).only("machine_specification__cpu_frequency")
            for fx in frequency_x:
                f_set.add(fx.machine_specification.cpu_frequency)

            f_list = list(f_set)
            f_list.append(compute_node.machine_specification.cpu_frequency)

            sorted(f_list)
            fid = f_list.index(compute_node.machine_specification.cpu_frequency)

            previous_id = fid - 1
            next_id = fid + 1

            if previous_id < 0:
                previous_id = 0
            if next_id >= len(f_list) -1:
                next_id = fid

            select_id = previous_id
            if abs(f_list[previous_id]-f_list[fid]) > abs(f_list[next_id]-f_list[fid]):
                if next_id != fid:
                    select_id = next_id

            ipx = models.ImageProcessingExperiment.objects(
                    machine_specification__cpu_frequency = f_list[select_id],
                    image_analysis=ip['name'],
                    video_size=video_size,
                    fps=fps
                    ).first()

        if ipx is None:
            ipx = models.ImageProcessingExperiment.objects(
                    image_analysis=ip['name'],
                    video_size=video_size,
                    fps=fps
                    ).first()

        if ipx:
            print("found cpu model:", ipx.machine_specification.cpu_model,
                  "especpted:", compute_node.machine_specification.cpu_model)
            print("name: %s video_size: %s fps: %s cpu: %s/%s"%
                    (ipx.image_analysis,"x".join(map(str, video_size)),
                        fps, ipx.machine_specification.cpu_frequency,
                        compute_node.machine_specification.cpu_frequency))

            cpu_usage, memory_usage = self.get_heuristic_resources(ipx)

            print("before cpu:", cpu_usage, "memory:", memory_usage)
            if ipx.machine_specification.cpu_model != compute_node.machine_specification.cpu_model\
                    and ipx.machine_specification.cpu_frequency != compute_node.machine_specification.cpu_frequency:
                factor = 1
                if ipx.machine_specification.cpu_frequency >=  compute_node.machine_specification.cpu_frequency:
                    factor = compute_node.machine_specification.cpu_frequency / ipx.machine_specification.cpu_frequency
                else:
                    factor = ipx.machine_specification.cpu_frequency / compute_node.machine_specification.cpu_frequency

                cpu_usage = cpu_usage * factor
                memory_usage = memory_usage * factor
            print("factor:",factor)
            print("cpu:", cpu_usage, "memory:", memory_usage)
        else:
            pass

        return cpu_usage, memory_usage

    def predict_processor_resource_usage(self, compute_node, processor, image_processors=None):


        cpu_usage = 0
        memory_usage = 0

        if image_processors is None:
            image_processors = processor.image_processors

        for ip in image_processors:
            if 'width' in ip:
                video_size = [ip['width'], ip['height']]

            cpu_usage, memory_usage = self.get_image_processing_experiment(compute_node, processor, ip)

            if 'image_processors' in ip:
                cpu_r, memory_r = self.predict_processor_resource_usage(compute_node,
                                                            processor,
                                                            ip['image_processors'])
                cpu_usage += cpu_r
                memory_usage += memory_r

        return cpu_usage, memory_usage


    def get_estimate_processor_on_compute_node(self, compute_node, processor=None):
        records = compute_node.resource_records
        cpu = []
        memory = []
        last = datetime.datetime.now()-datetime.timedelta(minutes=2)
        # last = datetime.datetime.now()-datetime.timedelta(days=1)
        for record in records:
            if record.reported_date > last:
                cpu.append(record.system_load.cpu)
                memory.append(record.system_load.memory)

        if len(cpu) <= 0:
            return None, None, None

        cpu_predict = self.get_predict_resource(cpu)
        memory_predict = self.get_predict_resource(memory)

        print('current system load:', cpu_predict, memory_predict)
        cpu_usage, memory_usage = cpu_predict, memory_predict

        processors = models.Processor.objects(operating__compute_node=compute_node,
                                              operating__user_command='run').all()
        counter = 0
        if processor:
            print("processor name:", processor.name)

        for p in processors:
            if p == processor:
                continue
            cpu_usage_p, memory_usage_p = self.predict_processor_resource_usage(compute_node, p);
            cpu_usage += cpu_usage_p
            memory_usage += memory_usage_p
            print("p name:", p.name)
            counter += 1
        print('got processor: ', counter)

        print('predict processor usage:', cpu_usage, memory_usage)

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
            # if self.is_suitable_running(compute_node, processor):
            return compute_node

    def is_suitable_running(self, compute_node, processor):
        if not hasattr(compute_node, "resource_records"):
            return False

        cn_cpu_usage, cn_memory_usage, cn_disk_usage \
                = self.predict_resource(compute_node)
        if cn_cpu_usage is None:
            return False

        processor_cpu_usage, processor_memory_usage \
                = self.predict_processor_resource_usage(compute_node, processor)
        print("p cpu: %s p memory: %s" % (processor_cpu_usage, processor_memory_usage))
        print("cn cpu: %s cn memory: %s cn disk: %s"%(cn_cpu_usage, cn_memory_usage, cn_disk_usage))

        # cpu_available = compute_node.machine_specification.cpu_count*100 - cn_cpu_usage
        # memory_available = compute_node.machine_specification.total_memory - cn_memory_usage
        # print("available cn cpu: %s cn memory: %s "%(cpu_available, m3mory_available))
        cn_p_cpu_usage, cn_p_memory_usage = self.get_estimate_processor_on_compute_node(compute_node, processor)

        # need policy
        cn_cpu_future = 0
        cn_memory_future = 0
        if cn_cpu_usage > cn_p_cpu_usage:
            cn_cpu_future = cn_cpu_usage + processor_cpu_usage
            cn_memory_future = cn_memory_usage + processor_memory_usage
        else:
            cn_cpu_future = cn_p_cpu_usage + processor_cpu_usage
            cn_memory_future = cn_p_memory_usage + processor_memory_usage

        print("last predict cn cpu: %s cn memory: %s"%(cn_cpu_future, cn_memory_future))

        print("suitable check: %s:%s"%(self.is_available_cpu(cn_cpu_future, compute_node.machine_specification.cpu_count),
                self.is_available_memory(cn_memory_future, compute_node.machine_specification.total_memory)))

        if self.is_available_cpu(cn_cpu_future,
                    compute_node.machine_specification.cpu_count) and \
                self.is_available_memory(cn_memory_future,
                    compute_node.machine_specification.total_memory) and \
                self.is_available_disk(cn_disk_usage,
                    compute_node.machine_specification.total_disk):
            return True

        return False



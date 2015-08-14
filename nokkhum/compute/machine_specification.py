

import platform
import psutil
import netifaces
import subprocess

import logging
logger = logging.getLogger(__name__)

class MachineSpecification:
    def __init__(self, path, interface='lo'):
        self.path = path
        self.ip = '124.0.0.1'

        try:
            self.ip = netifaces.ifaddresses(interface).setdefault(
                netifaces.AF_INET)[0]['addr']
        except:
            self.ip = netifaces.ifaddresses('lo').setdefault(
                netifaces.AF_INET)[0]['addr']

    def get_specification(self):

        mem = psutil.virtual_memory()
        cpu_frequency = 0
        cpu_model = ''

        try:
            cpuinfo = subprocess.check_output('lscpu')
            cpu_model = ''
            cpu_frequency = 0.0
            cpu_frequency_max = 0.0
            for line in cpuinfo.decode('utf-8').split('\n'):
                if 'CPU MHz' in line:
                    str_token = line.split(':')
                    cpu_frequency = float(str_token[1].strip())
                    continue

                if 'CPU max MHz' in line:
                    str_token = line.split(':')
                    cpu_frequency_max = float(str_token[1].strip())
                    continue

                if 'Model name' in line:
                    str_token = line.split(':')
                    cpu_model = str_token[1].strip()

                if len(cpu_model) > 0 and cpu_frequency > 0:
                    break

            if cpu_frequency_max > 0:
                cpu_frequency = cpu_frequency_max

        except Exception as e:
            logger.exception(e)

        disk = psutil.disk_usage(self.path)

        specification = {
            'name': platform.node(),
            'system': platform.system(),
            'machine': platform.machine(),
            'cpu_model': cpu_model,
            'cpu_count': psutil.cpu_count(),
            'cpu_frequency': cpu_frequency,
            'total_memory': mem.total,
            'total_disk': disk.total,
            'ip': self.ip
        }

        return specification

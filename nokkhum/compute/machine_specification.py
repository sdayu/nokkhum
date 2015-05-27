

import platform
import psutil
import fileinput
import netifaces

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

        mem = psutil.phymem_usage()
        cpu_frequency = 0
        cpu_model = ''

        try:
            cpuinfo = fileinput.input(files='/proc/cpuinfo')
            for line in cpuinfo:
                if 'cpu MHz' in line:
                    str_token = line.split(':')
                    cpu_frequency = float(str_token[1].strip())
                    continue

                if 'model name' in line:
                    str_token = line.split(':')
                    cpu_model = str_token[1].strip()

                if len(cpu_model) > 0 and cpu_frequency > 0:
                    break

            cpuinfo.close()
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

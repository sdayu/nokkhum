

import platform
import psutil
import fileinput

import logging
logger = logging.getLogger(__name__)

class MachineSpecification:
    def __init__(self, path):
        self.path = path

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
            'memory': mem.total,
            'disk': disk.total,
        }

        return specification

'''
Created on Jan 16, 2012

@author: boatkrap
'''
import subprocess
import json

from nokkhum import config

import logging
logger = logging.getLogger(__name__)


class ImageProcessor:

    def __init__(self, process_id):
        self.id = process_id
        self.programe_path = config.Configurator.settings.get(
            'nokkhum.processor.path')
        args = [self.programe_path, "--processor_id",
                str(self.id), "--log_dir", config.Configurator.settings.get('nokkhum.log_dir') + "/processors"]
        self.process = subprocess.Popen(args, shell=False,
                                        stdin=subprocess.PIPE,
                                        stdout=subprocess.PIPE,
                                        stderr=subprocess.PIPE)

    def start(self, surveillance_attibutes):

        arguments = {
            'action': 'start',
            # the configuration of processor need to config
            'attributes': surveillance_attibutes,
        }

        args = json.dumps(arguments)
        command = args + "\n"

        logger.debug("Start processor: %s" % command)

        self.process.stdin.write(command.encode('utf-8'))
        self.process.stdin.flush()

        if self.process.poll() is None:
            return self.process.stdout.readline().decode('utf-8')
        else:
            msg = self.process.stderr.readline().decode('utf-8')
            raise RuntimeError(msg)

    def stop(self):

        arguments = {'action': 'stop'}
        args = json.dumps(arguments)
        command = args + "\n"
        self.process.stdin.write(command.encode('utf-8'))
        self.process.stdin.flush()
        self.process.stdin.close()
        result = self.process.stdout.readline().decode('utf-8')
        self.process.wait()
        return result

    def get_attributes(self):

        arguments = {'action': 'get_attributes'}
        args = json.dumps(arguments)

        command = args + "\n"
        self.process.stdin.write(command.encode('utf-8'))
        self.process.stdin.flush()

        result = self.process.stdout.readline().decode('utf-8')

        return result

    def is_running(self):
        if self.process.poll() is None:
            return True
        else:
            return False
    
    def get_pid(self):
        if self.process:
            return self.process.pid
        
        return None

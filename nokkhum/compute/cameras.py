'''
Created on Jan 16, 2012

@author: boatkrap
'''
import subprocess
import json

from nokkhum import config

#import logging
#logger = logging.getLogger(__name__)


class Camera:
    def __init__(self, id):
        self.id = id
        self.programe_path = config.Configurator.settings.get('nokkhum.processor.path')
        args = [self.programe_path, "--camera_id", str(self.id), "--log_dir", config.Configurator.settings.get('nokkhum.log_dir')+"/processors"]
        self.process = subprocess.Popen(args, shell=False, \
                                        stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
    def start(self, surveillance_attibutes):
            
        arguments = {
                     'action':'start', 
                     'attributes':surveillance_attibutes, # the configuration of processor need to config
                     }
        
        args = json.dumps(arguments)
        command = args+"\n"
        self.process.stdin.write(command.encode('utf-8'))

        if self.process.poll() == None:
            return self.process.stdout.readline().decode('utf-8')
        else:
            msg = self.process.stderr.readline().decode('utf-8')
            raise RuntimeError(msg)

    def stop(self):

        arguments = {'action':'stop'}
        args = json.dumps(arguments)
        command = args+"\n"
        self.process.stdin.write(command.encode('utf-8'))
        self.process.stdin.close()
        result = self.process.stdout.readline().decode('utf-8')
        self.process.wait()
        return result
    
    def get_attributes(self):

        arguments = {'action':'get_attributes'}
        args = json.dumps(arguments)

        command = args+"\n"
        self.process.stdin.write(command.encode('utf-8'))

        result = self.process.stdout.readline().decode('utf-8')
            
        return result
    
    def is_running(self):
        if self.process.poll() is None:
            return True
        else:
            return False

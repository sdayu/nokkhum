'''
Created on Aug 21, 2012

@author: boatkrap
'''

from nokkhum import config
from nokkhum.cloud import vm

from nokkhum import models

import datetime, time

class VMManager(object):
    '''
    classdocs
    '''

    def __init__(self):
        settings = config.settings
        
        access_key_id       = settings.get('nokkhum.vm.ec2.access_key_id')
        secret_access_key   = settings.get('nokkhum.vm.ec2.secret_access_key')
        host                = settings.get('nokkhum.vm.ec2.host')
        port                = settings.get('nokkhum.vm.ec2.port')
        secure              = settings.get('nokkhum.vm.ec2.secure_connection')
        
        self.image_name = settings.get('nokkhum.vm.ec2.image.name')
        self.instance_type = [image.strip() for image in settings.get('nokkhum.vm.ec2.instance_type').split(',')]

        self.api = vm.ec2.EC2Client(access_key_id, secret_access_key, host, port, secure)
    
    def acquire(self):
        instance = None
        try:
            instance = self.api.start_instance(self.image_name, self.instance_type[0])
        except Exception as e:
            pass
        
        compute_node = models.ComputeNode()
        
        vm_info             = models.VMInstance()
        vm_info.image_id    = self.image_name[0]
        vm_info.instance_id = instance.id
        vm_info.instance_type = instance.instance_type
        vm_info.name        = instance.private_dns_name
        vm_info.ip_address  = instance.ip_address
        vm_info.kernel      = instance.kernel
        vm_info.ramdisk     = instance.ramdisk
        vm_info.private_ip_address = instance.private_ip_address
        vm_info.start_instance_date = datent(access_key_id, secret_access_key, host, port, secure)
        time.datetime.now() #instance.launch_time
    
        compute_node.name = vm_info.name
        compute_node.host = vm_info.private_ip_address
        compute_node.vm = vm_info
        compute_node.save()
        
        # need appropriate time to wait
        time.sleep(60)
        
        
    def terminate(self, instance_id):
        self.api.stop_instance(instance_id)
        compute_node = models.ComputeNode.objects(vm__instance_id=instance_id).first()
        compute_node.vm.terminate_instance_date = datetime.datetime.now()
        compute_node.save()
        
    def list_vm_compute_node(self):
        compute_nodes = models.ComputeNode.objects(vm__ne = None).all()
        return compute_nodes
    
    def list_vm_unavailable_compute_node(self):
        compute_nodes = models.ComputeNode.objects(vm__ne = None, ).all()
        return compute_nodes
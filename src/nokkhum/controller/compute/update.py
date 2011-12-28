'''
Created on Dec 23, 2011

@author: boatkrap
'''

import threading

from nokkhum.common.messages import consumer
import logging

logger = logging.getLogger(__name__)

class UpdateComputeNode(resource.Resource):

    def render_POST(self, request):
        result = dict()
        try:
            name        = request.args['name'][0]
            port        = request.args['port'][0]
            cpu_count   = request.args['cpu_count'][0]
            total_ram   = request.args['total_ram'][0]
            system      = request.args['system'][0]
            machine     = request.args['machine'][0]
            host        = request.getClientIP()
            
            logger.msg( 'Begin to update compute node name: ' + name)
            
            compute_node = models.ComputeNode.objects(name=name, host=host).first()
            if compute_node is None:
                compute_node = models.ComputeNode()
                compute_node.name = name
                compute_node.host = host
                
            cpu = models.CPUInfomation()
            cpu.count = cpu_count
            
            memory = models.MemoryInfomation()
            memory.total = total_ram
            
            compute_node.port    = port
            compute_node.machine = machine
            compute_node.system  = system
            compute_node.cpu     = cpu
            compute_node.memory  = memory
            compute_node.update_date = datetime.datetime.now()
            compute_node.save()
        
            result["result"] = "update ok"
            logger.msg( 'Compute node name: "%s" update complete' % ( name ) )
        except:
            logger.err()
            result["result"] = 'Update Compute Node Error'
        
        return json.dumps(result)
    
class UpdateComputeNodeStatus(resource.Resource):

    def render_POST(self, request):
        result = dict()
        try:
            name        = request.args['name'][0]
            cpu_str     = request.args['cpu'][0]
            memory_str  = request.args['memory'][0]
            cameras_str = request.args['cameras'][0]
            host        = request.getClientIP()
            
            compute_node = models.ComputeNode.objects(name=name, host=host).first()
            if compute_node is None:
                result["result"] = "Compute node is unavailable"
                return json.dumps(result)
            
            cpu     = json.loads(cpu_str)
            memory  = json.loads(memory_str)
            
            compute_node.cpu.usage   = cpu["usage"]
            compute_node.cpu.usage_per_cpu = cpu["percpu"]
            
            compute_node.memory.total = memory["total"]
            compute_node.memory.used  = memory["used"]
            compute_node.memory.free  = memory["free"]
            
            current_time = datetime.datetime.now()
            compute_node.update_date = current_time
            compute_node.save()
            
            print "camera_str: ", cameras_str
            cameras_id  = json.loads(cameras_str)
            for id in cameras_id:
                camera = models.Camera.objects().get(id=id)
                camera.operating.status = "Running"
                camera.operating.update_date = current_time
                camera.operating.compute_node = compute_node
                camera.save()
                
        
            result["result"] = "update success"
            log.msg( 'Compute node name: "%s" update stat complete' % ( name ) )
        except:
            log.err()
            result["result"] = 'Update Compute Node Stat Error'
        
        return json.dumps(result)


class UpdateStatus(threading.Thread):
    
    def __init__(self):
        threading.Thread.__init__(self)
        self._consumer = consumer.ConsumerFactory().get_consumer("nokkhum_compute.update_status")
        self.connection = consumer.ConsumerFactory().get_connection()
        self.update()
        self.daemon = True
        self._running = False
        
    def update(self):
        def process_msg(body, message):
            print body
            message.ack()
        
        self._consumer.register(process_msg)

        
    def run(self):

        self._running = True
        while self._running:
            self.connection.drain_events()
            
    def stop(self):
        self._running = False

    
    
    
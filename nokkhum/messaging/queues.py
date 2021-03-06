'''
Created on Dec 23, 2011

@author: boatkrap
'''
from kombu import Queue


class QueueFactory:

    def get_queue(self, exchange, routing_key):
        import fnmatch
        import re
        regex = fnmatch.translate('nokkhum_compute.*.rpc_request')
        reobj_rpc_request = re.compile(regex)
        regex = fnmatch.translate('nokkhum_compute.*.rpc_response')
        reobj_rpc_response = re.compile(regex)

        if routing_key == "nokkhum_compute.update_status":
            return Queue("nokkhum_compute.update_status", exchange, routing_key=routing_key)
        if "nokkhum_compute.*.rpc_" in routing_key:
            return
        elif reobj_rpc_request.match(routing_key):
            return Queue(routing_key, exchange, routing_key=routing_key, auto_delete=True)
        elif reobj_rpc_response.match(routing_key):
            # return Queue("nokkunm_compute.rpc_response", exchange,
            # routing_key=routing_key, auto_delete=True)
            return Queue(routing_key, exchange, routing_key=routing_key, auto_delete=True)
        else:
            return None

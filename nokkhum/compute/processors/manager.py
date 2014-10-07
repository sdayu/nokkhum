'''
Created on Oct 5, 2011

@author: boatkrap
'''
import logging
import time
logger = logging.getLogger(__name__)

import threading


class ProcessPolling(threading.Thread):

    def __init__(self, processor, output_list):
        self.processor = processor
        self.output_list = output_list
        self.running = True
        super().__init__()

    def run(self):
        time.sleep(5)
        while self.running:
            if self.processor.is_running():
                data = self.processor.process.stderr.readline().decode('utf-8')
                if len(data.strip()) == 0:
                    continue
                self.output_list.append(data)
            else:
                logger.debug(
                    "ProcessPolling camera id: %s terminate" % (self.processor.id))
                break


class ProcessorManager:

    def __init__(self):
        self.pool = dict()
        self.thread_pool = dict()
        self.output = dict()

    def add(self, processor_id, processor):
        if processor_id not in self.pool.keys():
            self.pool[processor_id] = processor
            self.output[processor_id] = []
            self.thread_pool[processor_id] = ProcessPolling(
                processor, self.output[processor_id])
            self.thread_pool[processor_id].start()

    def delete(self, processor_id):
        if processor_id in self.pool.keys():
            del self.pool[processor_id]

            self.thread_pool[processor_id].running = False
            self.thread_pool[processor_id].join()
            del self.thread_pool[processor_id]

            del self.output[processor_id]

    def get(self, processor_id):
        if processor_id in self.pool.keys():
            return self.pool[processor_id]
        else:
            return None

    def get_pool(self):
        return self.pool

    def list_processors(self):
        return self.pool.keys()

    def available(self):
        avialable_process = []
        for k, v in self.pool.items():
            if v.is_running():
                avialable_process.append(k)

        return avialable_process

    def read_process_output(self, processor_id):
        results = []

        if processor_id in self.pool.keys():
            while len(self.output[processor_id]) > 0:
                message = self.output[processor_id].pop()
                logger.debug("processor id=%s :%s" % (processor_id, message))
                results.append(message)

                if len(self.output[processor_id]) > 10:
                    logger.debug("slice output to 10")

                    while len(self.output[processor_id]) > 10:
                        self.output[processor_id].pop()

        return results

    def remove_dead_process(self):
        dead_process = {}

        remove_process = [
            k for k, v in self.pool.items() if not v.is_running()]

        # try to remove dead process
        for key in remove_process:
            processor_process = self.pool[key]
            if not processor_process.is_running():
                result = ""
                try:
                    for line in processor_process.process.stdout:
                        result += line.decode('utf-8')
                    for line in processor_process.process.stderr:
                        result += line.decode('utf-8')
                except Exception as e:
                    logger.exception(e)

                if key in self.output:
                    if key in self.thread_pool:
                        self.thread_pool[key].running = False

                    while len(self.output[key]) > 0:
                        result += (self.output[key].pop() + "\n")

                if len(result) == 0:
                    result = "Process exist with Unknown Message"
                dead_process[key] = result
                self.delete(key)

        logger.debug("remove: %s", dead_process)
        return dead_process

    def get_pids(self):
        pids = []
        for k, v in self.pool.items():
            pids.append((v.process.pid, k))

        return pids

'''
Created on Dec 1, 2011

@author: boatkrap
'''

import threading
import datetime

import logging
logger = logging.getLogger(__name__)

from nokkhum import models

class ProcessorMonitoring(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.name = "ImageProcessor Monitoring"
        self.daemon = True
        self.maximum_wait_time = 60 # in second
        
    def run(self):
        
        logger.debug("ImageProcessor Monitoring working")
        self.__monitor_processor_active()
        logger.debug("ImageProcessor Monitoring terminate")
        
    def __request_new_processor_command(self, processor, action, message):
        processor_command = models.ProcessorCommand.objects(processor=processor, action=action, status='waiting').first()

        if processor_command is not None:
            return
      
        new_command = models.ProcessorCommand()
        new_command.extra['last_status'] = processor.operating.status
        if processor.operating.status == "running" or processor.operating.status == "starting" \
                or processor.operating.status == "fail":
            if processor.operating.user_command == 'stop' \
                or processor.operating.user_command == 'suspend':
                processor.operating.status = 'stop'
                processor.operating.user_command = 'stop'
                processor.save()
                return
                
            new_command.action = "start"
            processor.operating.status = "start"
            processor.save()
        elif processor.operating.status == "stopping":
            new_command.action = "stop"
        
        new_command.processor = processor
        new_command.message = message
        new_command.command_type = 'system'
        new_command.command_date = datetime.datetime.now()
        new_command.update_date = datetime.datetime.now()
        new_command.message += "\n\nextra: %s"%new_command.extra
        new_command.save()
        
        this_queue = models.ProcessorCommandQueue()
        this_queue.processor_command = new_command
        this_queue.save()
        
    def __monitor_processor_active(self):
        processors = models.Processor.objects(status='active').all()
        # logger.debug("processors count: %d"%len(processors))
        current_time = datetime.datetime.now()
        for processor in processors:
            if processor.operating.user_command == "run":
                if processor.operating.status == "running" or processor.operating.status == "starting":
                    diff_time = current_time - processor.operating.update_date
                    logger.debug( "processor id: %s diff: %d s" % (processor.id, diff_time.total_seconds()))
                    if diff_time > datetime.timedelta(seconds=self.maximum_wait_time):
                        logger.debug( "processor id: %s disconnect diff: %d s" % (processor.id, diff_time.total_seconds()))
                        message = "Processor disconnect.\n Restart processor by ProcessorMonotoring: %s" % datetime.datetime.now()
                        self.__request_new_processor_command(processor, "start", message)
                elif processor.operating.status == "fail":
                    logger.debug( "processor id: %s status fail"%processor.id)
                    message = "Processor run fail.\n Restart processor by ProcessorMonotoring: %s" % datetime.datetime.now()
                    self.__request_new_processor_command(processor, "start", message)
                    
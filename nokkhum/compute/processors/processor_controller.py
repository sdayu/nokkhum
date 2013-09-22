'''
Created on Sep 9, 2011

@author: boatkrap
'''

from nokkhum import config
from nokkhum.compute import processor_manager
from . import processors

import logging
logger = logging.getLogger(__name__)

class ProcessorController():
    def list_processors(self):
        '''
        List working processor
        '''
        logger.debug('List Processors')
        
        respons = {'success': False}
        processor_list = list()
        for process_name in processor_manager.pool:
            processor_list.append(process_name)
        
        respons['success'] = True
        respons['result'] = processor_list
        
        return respons
    

    def get_processor_attributes(self, processor_id):
        '''
        List working processor resource
        '''
        logger.debug('Get Processors Attributes')
        
        respons = {'success': False}
        try:
            processor_process = processor_manager.get(processor_id)
            if processor_process == None:
                logger.debug( 'processor id: %s is not available' % ( processor_id ) )
                respons["comment"] = 'processor id: %s is not available' % ( processor_id )
                return respons
            
            respons['success'] = True
            respons["result"] = processor_process.get_attributes()
        
        except Exception as e:
            logger.exception(e)
            respons["comment"] = 'Get Processor Attribute Error'
            
        return respons

    def start_processor(self, processor_id, surveillance_attibutes):
        '''
        start to add processor
        '''
        respons = {'success': False}
        try:
            is_available = processor_manager.get(processor_id)
            
            if is_available != None:
                respons["comment"] = "processor id: %s cannot start because is available" % processor_id
                logger.debug( 'processor id: %s can not start, it is available ' % ( processor_id ) )
                return respons
            
            logger.debug( 'Begin to start processor')
            logger.debug( "processor_id: %s"%processor_id)
            
            default_path = "%s/%s" % (config.Configurator.settings.get('nokkhum.processor.record_path'), processor_id)
        
            def change_default_record(image_processors):
                for image_processor in image_processors:
                    if 'Recorder' in image_processor["name"]:
                        image_processor["directory"] = default_path
                        
                    if "image_processors" in image_processor and len(image_processor["image_processors"]) > 0:
                        change_default_record(image_processor["image_processors"])
                    
            change_default_record(surveillance_attibutes["image_processors"])
            
            logger.debug( "surveillance_attibutes: %s"%surveillance_attibutes)
            
            processor_process = processors.ImageProcessor(processor_id)
            logger.debug( "start VS for processor id: %s", processor_id);
            respons["comment"] = processor_process.start(surveillance_attibutes)
            logger.debug( "add process processor id: %s to process manager", processor_id);
            processor_manager.add( processor_id, processor_process )
             
            respons["success"] = True

            logger.debug( 'Processor id: %s started' % ( processor_id ) )
        except Exception as e:
            logger.exception(e)
            respons["comment"] = 'Add Processor Error'
            logger.debug( 'Processor name: %s started error' % ( processor_id ) )
        
        return respons

    def stop_processor(self, processor_id):
        '''
        stop processing and remove from processor pool
        '''
        
        respons = {'success': False}
#        logger.debug("pool: %s"%processor_manager.pool)
        try:
            processor_process = processor_manager.get(processor_id)
            if processor_process == None:
                logger.debug( 'processor id: %s is not available' % ( processor_id ) )
                respons["comment"] = 'processor id: %s is not available' % ( processor_id )
                return respons
#            logger.debug("try to stop: %s"%processor_process)
            respons["comment"] = processor_process.stop()
            respons["success"] = True
            processor_manager.delete(processor_id)
            logger.debug( 'Processor name: %s deleted' % ( processor_id ) )
        except Exception as e:
            logger.exception(e)
            respons["comment"] = 'Delete Processor Error'
            
        return respons
    
    def stop_all(self):
        for processor_id in processor_manager.list_processors():
            self.stop_processor(processor_id)
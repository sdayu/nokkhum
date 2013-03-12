'''
Created on Sep 9, 2011

@author: boatkrap
'''

from nokkhum import config
from nokkhum.compute import processor_manager
from . import cameras

import logging
logger = logging.getLogger(__name__)

class CameraController():
    def list_camera(self):
        '''
        List working camera resource
        '''
        logger.debug('List Cameras')
        
        respons = {'success': False}
        camera_list = list()
        for process_name in processor_manager.pool:
            camera_list.append(process_name)
        
        respons['success'] = True
        respons['result'] = camera_list
        
        return respons
    

    def get_cameras_attributes(self, camera_id):
        '''
        List working camera resource
        '''
        logger.debug('Get Cameras Attributes')
        
        respons = {'success': False}
        try:
            camera_process = processor_manager.get(camera_id)
            if camera_process == None:
                logger.debug( 'camera id: %s is not available' % ( camera_id ) )
                respons["comment"] = 'camera id: %s is not available' % ( camera_id )
                return respons
            
            respons['success'] = True
            respons["result"] = camera_process.get_attributes()
        
        except Exception as e:
            logger.exception(e)
            respons["comment"] = 'Get Camera Attribute Error'
            
        return respons

    def start_camera(self, camera_id, surveillance_attibutes):
        '''
        start to add camera
        '''
        respons = {'success': False}
        try:
            is_available = processor_manager.get(camera_id)
            
            if is_available != None:
                respons["comment"] = "camera id: %d cannot start because is available" % camera_id
                logger.debug( 'camera id: %s can not start, it is available ' % ( camera_id ) )
                return respons
            
            logger.debug( 'Begin to start camera')
            logger.debug( "camera_id: %d"%camera_id)
            
            default_path = "%s/%d" % (config.Configurator.settings.get('nokkhum.processor.record_path'), camera_id)
        
            def change_default_record(processors):
                for processor in processors:
                    if 'Recorder' in processor["name"]:
                        processor["directory"] = default_path
                        
                    if "processors" in processor and len(processor["processors"]) > 0:
                        change_default_record(processor["processors"])
                    
            change_default_record(surveillance_attibutes["processors"])
            
            logger.debug( "surveillance_attibutes: %s"%surveillance_attibutes)
            
            camera_process = cameras.Camera(camera_id)
            logger.debug( "start VS for camera id: %s", camera_id);
            respons["comment"] = camera_process.start(surveillance_attibutes)
            logger.debug( "add process camera id: %s to process manager", camera_id);
            processor_manager.add( int(camera_id), camera_process )
             
            respons["success"] = True

            logger.debug( 'Camera name: %s started' % ( camera_id ) )
        except Exception as e:
            logger.exception(e)
            respons["comment"] = 'Add Camera Error'
            logger.debug( 'Camera name: %s started error' % ( camera_id ) )
        
        return respons

    def stop_camera(self, camera_id):
        '''
        stop processing and remove from processor pool
        '''
        
        respons = {'success': False}
#        logger.debug("pool: %s"%processor_manager.pool)
        try:
            camera_process = processor_manager.get(camera_id)
            if camera_process == None:
                logger.debug( 'camera id: %s is not available' % ( camera_id ) )
                respons["comment"] = 'camera id: %s is not available' % ( camera_id )
                return respons
#            logger.debug("try to stop: %s"%camera_process)
            respons["comment"] = camera_process.stop()
            respons["success"] = True
            processor_manager.delete(camera_id)
            logger.debug( 'Camera name: %s deleted' % ( camera_id ) )
        except Exception as e:
            logger.exception(e)
            respons["comment"] = 'Delete Camera Error'
            
        return respons
    
    def stop_all(self):
        for camera_id in processor_manager.list_camera():
            self.stop_camera(camera_id)
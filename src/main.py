'''
Created on Sep 7, 2011

@author: boatkrap
'''
import sys, errno, os
import datetime

import logging
import logging.config

from nokkhum import controller
from nokkhum import models
from nokkhum import config

if __name__ == '__main__':
    if len(sys.argv) < 2:
        sys.stderr.write( "Use: " + sys.argv[0] + " configure_file")
        sys.exit(errno.EINVAL)
        
    config.settings = config.Configurator(sys.argv[1])
        
    models.initial(config.settings)   
    
    directory = config.settings.get('nokkhum.log_dir')
    if not os.path.exists(directory):
        os.makedirs(directory)
    
    wellcome_message = 'Starting nokkhum controller server: %s\n' % str(datetime.datetime.now())
    print wellcome_message
    
    logging.config.fileConfig(sys.argv[1])
    logger = logging.getLogger()
    logger.debug(wellcome_message)

    from nokkhum.messaging import connection
    connection.initial(config.settings.get('amq.url'))
    
    from nokkhum.controller import api
    controller_api = api.ControllerApi()
    

    try:
        controller_api.start()
    except KeyboardInterrupt:
        logger.debug("KeyboardInterrupt")
    except Exception as e:
        logger.exception(e)
    finally:
        controller_api.stop()
        
    logger.debug("Program Terminate")
    print "\nProgram Terminate"
    
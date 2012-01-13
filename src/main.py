'''
Created on Sep 7, 2011

@author: boatkrap
'''
import sys, errno, os
import datetime
import ConfigParser

import logging
import logging.config

from nokkhum import controller
from nokkhum.common import models
from nokkhum.controller import schedule

if __name__ == '__main__':
    if len(sys.argv) < 2:
        sys.stderr.write( "Use: " + sys.argv[0] + " configure_file")
        sys.exit(errno.EINVAL)
        
    config = ConfigParser.ConfigParser()
    config.read(sys.argv[1])
    
    controller.config = config
    setting = dict()
    for k, v in config.items("controller"):
        setting[k] = v
        
    models.initial(setting)   
    
    directory = controller.config.get('controller', 'nokkhum.controller.log_dir')
    if not os.path.exists(directory):
        os.makedirs(directory)
    
    wellcome_message = 'Starting nokkhum controller server: %s' % str(datetime.datetime.now())
    print wellcome_message
    
    logging.config.fileConfig(sys.argv[1])
    
    logger = logging.getLogger(__name__)
    logger.debug(wellcome_message)

    from nokkhum.controller import api
    
    controller_api = api.ControllerApi()
    controller_api.start()
    
    timer = schedule.timer.Timer()
    timer.start()
    
    try:
        timer.join()
    except KeyboardInterrupt:
        timer.stop()
    
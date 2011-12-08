'''
Created on Sep 7, 2011

@author: boatkrap
'''
import sys, errno, os
import datetime
import ConfigParser

from twisted.python import log
from twisted.python.logfile import DailyLogFile

from nokkhum import controller
from nokkhum.controller.services import services
from nokkhum import model
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
        
    model.initial(setting)   
    
    directory = os.path.dirname(controller.config.get('controller', 'nokkhum.controller.log_dir'))
    if not os.path.exists(directory):
        os.makedirs(directory)
        
    print 'Starting nokkhum controller server: %s' % str(datetime.datetime.now())

    log.startLogging(DailyLogFile.fromFullPath(controller.config.get('controller', 'nokkhum.controller.log_dir')))
    
    timer = schedule.timer.Timer()
    timer.start()
    
    services.start()
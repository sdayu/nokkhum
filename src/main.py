'''
Created on Sep 7, 2011

@author: boatkrap
'''
import sys, errno
import ConfigParser

from nokkhum import controller
from nokkhum.controller import services
from nokkhum import model

if __name__ == '__main__':
    if len(sys.argv) < 2:
        sys.stderr.write( "Use: " + sys.argv[0] + " configure_file")
        sys.exit(errno.EINVAL)
        
    config = ConfigParser.ConfigParser()
    config.read(sys.argv[1])
    
    controller.config = config
    
    model.initial(config)   
    services.start()
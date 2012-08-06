'''
Created on Aug 2, 2012

@author: boatkrap
'''
import threading

class VmScheduling(threading.Thread):
    def __init__(self):
        ''''''
        threading.Thread.__init__(self)
        self.name = "VM Scheduling"
        self.daemon = True
        
    def run(self):
        ''''''
        
    
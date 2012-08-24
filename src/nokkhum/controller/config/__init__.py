import ConfigParser

class Configurator:
    def __init__(self, config_file):
        self.config_file = config_file
        self.setting = dict()
        self.__parse()
    
    def __parse(self):
        config_parser = ConfigParser.ConfigParser()
        config_parser.read(self.config_file)
        
        section = "controller"

        boolean_conf    = ['nokkhum.compute.push_s3', 'nokkhum.s3.secure_connection', 'nokkhum.ec2.secure_connection', 'nokkhum.vm.enable']
        integer_conf    = ['nokkhum.s3.port', 'nokkhum.ec2.port']
        
        self.setting['nokkhum.vm.enable'] = False
        
        for k, v in config_parser.items(section):
            if k in boolean_conf:
                self.setting[k] = config_parser.getboolean(section, k)
            elif k in integer_conf:
                self.setting[k] = config_parser.getint(section, k)
            else:
                self.setting[k] = v
                
    def get(self, key):
        if key not in self.setting:
            return None
        
        return self.setting[key]



        
        
        
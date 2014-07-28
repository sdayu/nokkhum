import configparser


class Configurator:
    settings = dict()

    def __init__(self, config_file):
        self.config_file = config_file
        self.__parse()

    def __parse(self):
        config_parser = configparser.ConfigParser()
        config_parser.read(self.config_file)

        sections = ["controller", "compute"]

        boolean_conf = ['nokkhum.storage.enable',
                        'nokkhum.storage.s3.secure_connection',
                        'nokkhum.vm.ec2.secure_connection',
                        'nokkhum.vm.enable',
                        'nokkhum.smtp.tls']
        integer_conf = ['nokkhum.storage.s3.port',
                        'nokkhum.vm.ec2.port',
                        'nokkhum.smtp.port']

        for key in boolean_conf:
            self.settings[key] = False

        for section in sections:
            if not config_parser.has_section(section):
                continue

            for k, v in config_parser.items(section):
                if k in boolean_conf:
                    self.settings[k] = config_parser.getboolean(section, k)
                elif k in integer_conf:
                    self.settings[k] = config_parser.getint(section, k)
                else:
                    self.settings[k] = v

    def get(self, key):
        if key not in self.settings:
            return None

        return self.settings[key]

    def keys(self):
        return self.settings.keys()

    def items(self):
        return self.settings.items()

    def set(self, key, value):
        self.settings[key] = value

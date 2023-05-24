from configparser import ConfigParser
class Configer(object):
    def __init__(self,conf_path:str="./default.conf"):
        self.config = ConfigParser()
        self.config.read(conf_path,encoding='utf-8')

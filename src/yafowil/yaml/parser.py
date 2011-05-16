import yaml
import yafowil.loader
from yaml.parser import ParserError
from yafowil.base import factory

def parse_from_YAML(path, context=None):
    return YAMLParser(path, context)()


class YAMLTransformationError(Exception):
    """Raised if yafowil widget tree could not be build by YAML definitions.
    """


class YAMLParser(object):
    
    def __init__(self, path, context=None):
        self.path = path
        self.context = context
    
    def __call__(self):
        raw = None
        try:
            with open(self.path, 'r') as file:
                raw = yaml.load(file.read())
        except ParserError, e:
            msg = u"Cannot parse YAML from given path '%s'" % self.path
            raise YAMLTransformationError(msg)
        except IOError, e:
            msg = u"File not found: '%s'" % self.path
            raise YAMLTransformationError(msg)
        return self.create_tree(raw)
    
    def create_tree(self, data):
        pass
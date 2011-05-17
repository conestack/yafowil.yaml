import sys
import types
import yaml
import yafowil.loader
from yaml.parser import ParserError
from yafowil.base import (
    factory,
    UNSET,
)


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
        def call_factory(defs):
            props = dict()
            for k, v in defs.get('props', dict()).items():
                props[k] = self.parse_definition_value(v)
            custom = dict()
            for custom_key, custom_value in defs.get('custom', dict()).items():
                custom_props = list()
                for key in ['extractors',
                            'renderers',
                            'preprocessors',
                            'builders']:
                    part = custom_value.get(key, [])
                    if not type(part) in [types.TupleType, types.ListType]:
                        part = [part]
                    part = [self.parse_definition_value(pt) for pt in part]
                    custom_props.append(part)
                custom[custom_key] = custom_props
            return factory(
                defs.get('factory', 'form'), # defaults to 'form'
                name=defs.get('name', None),
                value=self.parse_definition_value(defs.get('value', UNSET)),
                props=props,
                custom=custom,
            )
        def create_children(node, children_defs):
            for child in children_defs:
                name = child.keys()[0]
                child_def = child[name]
                node[name] = call_factory(child_def)
                create_children(node[name], child_def.get('widgets', []))
        root = call_factory(data)
        create_children(root, data.get('widgets', []))
        return root
    
    def parse_definition_value(self, value):
        if not isinstance(value, basestring) or not '.' in value:
            return value
        names = value.split('.')
        bound = False
        if names[0] == 'context':
            bound = True
            part = self.context
        else:
            try:
                part = sys.modules[names[0]]
            except KeyError:
                return value
        for name in names[1:]:
            if name in part.__class__.__dict__.keys():
                part = part.__class__.__dict__[name]
                continue
            found = False
            for cls in part.__class__.__bases__:
                if name in cls.__dict__.keys():
                    part = cls.__dict__[name]
                    found = True
                    break
            if found:
                continue
            return value
        if not type(part) is types.FunctionType:
            return value
        if bound:
            return types.MethodType(part, self.context, self.context.__class__)
        return part
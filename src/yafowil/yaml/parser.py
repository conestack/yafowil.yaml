import os
import sys
import types
import pkg_resources
import yaml
import yafowil.loader  # nopep8  # loads registry
from yaml.error import YAMLError
from yafowil.base import (
    factory,
    UNSET,
)


def translate_path(path):
    if path.find(':') > -1:
        package, subpath = path.split(':')
        path = pkg_resources.resource_filename(package, subpath)
    return path


def parse_from_YAML(path, context=None, message_factory=None):
    return YAMLParser(translate_path(path), context, message_factory)()


class YAMLTransformationError(Exception):
    """Raised if yafowil widget tree could not be build by YAML definitions.
    """


class TBSupplement(object):

    def __init__(self, obj, msg):
        self.manageable_object = obj
        self.msg = msg

    def getInfo(self, html=1):
        return html and '<pre>{0}</pre>'.format(self.msg or self.msg)


class YAMLParser(object):

    def __init__(self, path, context=None, message_factory=None):
        self.path = path
        self.context = context
        self.message_factory = message_factory

    def __call__(self):
        return self.create_tree(self.load_yaml(self.path))

    def load_yaml(self, path):
        data = None
        try:
            with open(path, 'r') as file:
                data = yaml.load(file.read())
        except YAMLError, e:
            msg = u"Cannot parse YAML from given path '{0}'. " +\
                  u"Original exception was:\n{1}: {2}"
            msg = msg.format(path, e.__class__.__name__, e)
            raise YAMLTransformationError(msg)
        except IOError, e:
            msg = u"File not found: '{0}'".format(path)
            raise YAMLTransformationError(msg)
        return data

    def create_tree(self, data):
        def call_factory(defs):
            props = dict()
            for k, v in defs.get('props', dict()).items():
                props[k] = self.parse_definition_value(v)
            custom = dict()
            for custom_key, custom_value in defs.get('custom', dict()).items():
                custom_props = list()
                for key in ['extractors',
                            'edit_renderers',
                            'preprocessors',
                            'builders'
                            'display_renderers']:
                    part = custom_value.get(key, [])
                    if not type(part) in [types.TupleType, types.ListType]:
                        part = [part]
                    part = [self.parse_definition_value(pt) for pt in part]
                    custom_props.append(part)
                custom[custom_key] = custom_props
            return factory(
                defs.get('factory', 'form'),  # defaults to 'form'
                name=defs.get('name', None),
                value=self.parse_definition_value(defs.get('value', UNSET)),
                props=props,
                custom=custom,
                mode=self.parse_definition_value(defs.get('mode', 'edit')),
            )
        def create_children(node, children_defs):
            for child in children_defs:
                name = child.keys()[0]
                child_def = child[name]
                child_def['name'] = name
                # sub form nesting
                nest = child_def.get('nest')
                if nest:
                    nest_path = translate_path(nest)
                    # case same directory as main form yaml
                    if len([it for it in os.path.split(nest_path) if it]) == 1:
                        base_path = self.path.split(os.path.sep)[:-1]
                        nest_path = [os.path.sep] + base_path + [nest_path]
                        nest_path = os.path.join(*nest_path)
                    node[name] = self.create_tree(self.load_yaml(nest_path))
                # regular child parsing
                else:
                    node[name] = call_factory(child_def)
                    create_children(node[name], child_def.get('widgets', []))
        root = call_factory(data)
        create_children(root, data.get('widgets', []))
        return root

    def parse_definition_value(self, value):
        if not isinstance(value, basestring):
            return value
        if value.startswith('expr:'):
            def fetch_value(widget=None, data=None):
                __traceback_supplement__ = (TBSupplement, self, str(value))
                return eval(value[5:],
                            {'context': self.context, 'widget': widget,
                             'data': data}, {})
            return fetch_value
        if value.startswith('i18n:'):
            parts = value.split(":")
            if len(parts) > 3:
                raise YAMLTransformationError('to many : in {0}'.format(value))
            if len(parts) == 2:
                return self.message_factory(parts[1])
            return self.message_factory(parts[1], default=parts[2])
        if not '.' in value:
            return value
        names = value.split('.')
        if names[0] == 'context':
            part = self.context
        else:
            try:
                part = sys.modules[names[0]]
            except KeyError:
                return value
        for name in names[1:]:
            if hasattr(part, name):
                part = getattr(part, name)
            else:
                return value
        if not callable(part):
            return value
        return part

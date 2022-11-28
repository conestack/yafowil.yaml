# -*- coding: utf-8 -*-
from node.utils import UNSET
from yafowil.base import factory
from yafowil.compat import ITER_TYPES
from yafowil.compat import STR_TYPE
from yaml.error import YAMLError
import json
import os
import pkg_resources
import sys
import yafowil.loader  # noqa  # loads registry
import yaml


def translate_path(path):
    if path.find(':') > -1:
        package, subpath = path.split(':')
        path = pkg_resources.resource_filename(package, subpath)
    return path


def parse_from_YAML(
    path,
    context=None,
    message_factory=None,
    expression_globals={}
):
    return YAMLParser(
        translate_path(path),
        context,
        message_factory,
        expression_globals
    )()


class CommonTransformationError(Exception):
    """Raised if yafowil widget tree could not be build by YAML definitions.
    """


class YAMLTransformationError(CommonTransformationError):
    """Raised if yafowil widget tree could not be build by YAML definitions.
    """


class JSONTransformationError(CommonTransformationError):
    """Raised if yafowil widget tree could not be build by JSON definitions.
    """


class TBSupplement(object):

    def __init__(self, obj, msg):
        self.manageable_object = obj
        self.msg = msg

    def getInfo(self, html=1):
        return html and '<pre>{0}</pre>'.format(self.msg or self.msg)


python_expression_globals = {}


class YAMLParser(object):

    def __init__(
        self,
        path,
        context=None,
        message_factory=None,
        expression_globals={}
    ):
        self.path = path
        self.context = context
        self.message_factory = message_factory
        self.expression_globals = expression_globals

    def __call__(self):
        return self.create_tree(self.load(self.path))

    def load(self, path):
        if path.endswith('json'):
            # we support json too
            return self.load_json(path)
        return self.load_yaml(path)

    def load_json(self, path):
        data = None
        try:
            with open(path, 'r') as file:
                data = json.load(file)
        except (SyntaxError, ValueError) as e:
            msg = (
                u"Cannot parse JSON from given path '{0}'. "
                u"Original exception was:\n{1}: {2}"
            ).format(path, e.__class__.__name__, e)
            raise JSONTransformationError(msg)
        except IOError:
            msg = u"File not found: '{0}'".format(path)
            raise JSONTransformationError(msg)
        return data

    def load_yaml(self, path):
        data = None
        try:
            with open(path, 'r') as file:
                data = yaml.load(file.read(), yaml.SafeLoader)
        except YAMLError as e:
            msg = (
                u"Cannot parse YAML from given path '{0}'. "
                u"Original exception was:\n{1}: {2}"
            ).format(path, e.__class__.__name__, e)
            raise YAMLTransformationError(msg)
        except IOError:
            msg = u"File not found: '{0}'".format(path)
            raise YAMLTransformationError(msg)
        return data

    def create_tree(self, data):
        def call_factory(defs):
            props = dict()
            props = self.parse_attribute(defs.get('props', dict()))
            custom = dict()
            for custom_key, custom_value in defs.get('custom', dict()).items():
                custom_props = list()
                for key in [
                    'extractors',
                    'edit_renderers',
                    'preprocessors',
                    'builders',
                    'display_renderers'
                ]:
                    part = custom_value.get(key, [])
                    if not type(part) in ITER_TYPES:
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
                for key in child:
                    name = key
                    break
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
                    node[name] = self.create_tree(self.load(nest_path))
                # regular child parsing
                else:
                    node[name] = call_factory(child_def)
                    create_children(node[name], child_def.get('widgets', []))
        root = call_factory(data)
        create_children(root, data.get('widgets', []))
        return root

    def parse_attribute(self, value):
        if not isinstance(value, dict):
            return self.parse_definition_value(value)
        for k, v in value.items():
            if isinstance(v, dict):
                self.parse_attribute(v)
            else:
                value[k] = self.parse_definition_value(v)
        return value

    def parse_definition_value(self, value):
        if not isinstance(value, STR_TYPE):
            return value
        if value.startswith('python:'):
            expression_globals = {}
            expression_globals.update(python_expression_globals)
            expression_globals.update(self.expression_globals)
            return eval(value[7:], expression_globals, {})
        elif value.startswith('expr:'):
            def fetch_value(widget=None, data=None):
                __traceback_supplement__ = (TBSupplement, self, str(value))
                expression_globals = dict(
                    context=self.context,
                    widget=widget,
                    data=data
                )
                return eval(value[5:], expression_globals, {})
            return fetch_value
        elif value.startswith('i18n:'):
            parts = value.split(":")
            if len(parts) > 3:
                raise YAMLTransformationError('to many : in {0}'.format(value))
            if len(parts) == 2:
                return self.message_factory(parts[1])
            return self.message_factory(parts[1], default=parts[2])
        elif '.' not in value:
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

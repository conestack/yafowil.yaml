# -*- coding: utf-8 -*-
from uuid import UUID
from yafowil.tests import YafowilTestCase
from yafowil.tests import fxml
from yafowil.yaml import YAMLParser
from yafowil.yaml import parse_from_YAML
from yafowil.yaml import python_expression_globals
from yafowil.yaml.parser import JSONTransformationError
from yafowil.yaml.parser import YAMLTransformationError
import doctest
import os
import shutil
import tempfile
import unittest
import yaml


def _(msg, default=None):
    # dummy message factory
    return default or msg


def pxml(xml):
    print(fxml(xml))


class DummyContext(object):
    some_attr = ''

    @property
    def fail_callback(self):
        raise ValueError('I am supposed to fail')

    def firstfield_value(self, widget, data):
        return 'First value'

    def custom_extractor_1(self, widget, data):
        return data.extracted

    def custom_extractor_2(self, widget, data):
        return data.extracted

    def custom_renderer(self, widget, data):
        return data.rendered

    class NewStyle(object):
        class Another(object):
            def test_method_1(self, widget, data):
                return 'Test method 1'

        class OldStyle:
            def test_method_2(self, widget, data):
                return 'Test method 2'

        old_style = OldStyle()

    new_style = NewStyle()


def test_vocab(widget, data):
    return ['a', 'b', 'c']


class TestYAML(YafowilTestCase):

    def setUp(self):
        super(TestYAML, self).setUp()
        self.tempdir = tempfile.mkdtemp()

    def tearDown(self):
        super(TestYAML, self).tearDown()
        shutil.rmtree(self.tempdir)

    # Sample form definition
    yaml_tmpl = """
        factory: form
        name: demoform
        props:
            action: demoaction
        widgets:
        - firstfield:
            factory: field:label:error:text
            value: context.firstfield_value
            props:
                label: i18n:First Field
                description: I am the description
                required: I am required
                data:
                    flat: I am a flat data-attribute
                    i18n: i18n:nested_firstfield:i18n Nested First Field
                    nested:
                        nested-i18n: i18n:nested_firstfield:i18n Nested First Field
        - secondfield:
            factory: field:label:*custom_stuff:error:select
            value: ['a', 'b']
            props:
                label.title: i18n:second_field:Second Field
                multivalued: True
                vocabulary: yafowil.yaml.tests.test_vocab
            custom:
                custom_stuff:
                    extractors:
                        - context.custom_extractor_1
                        - context.custom_extractor_2
                    edit_renderers: context.custom_renderer
    """

    def test_load_yaml(self):
        self.assertEqual(yaml.load(self.yaml_tmpl, yaml.SafeLoader), {
            'factory': 'form',
            'name': 'demoform',
            'props': {
                'action': 'demoaction'
            },
            'widgets': [{
                'firstfield': {
                    'factory': 'field:label:error:text',
                    'value': 'context.firstfield_value',
                    'props': {
                        'description': 'I am the description',
                        'label': 'i18n:First Field',
                        'required': 'I am required',
                        'data': {
                            'flat': 'I am a flat data-attribute',
                            'i18n': 'i18n:nested_firstfield:i18n Nested First Field',
                            'nested': {
                                'nested-i18n': 'i18n:nested_firstfield:i18n Nested First Field'
                            }
                        }
                    }
                }
            }, {
                'secondfield': {
                    'factory': 'field:label:*custom_stuff:error:select',
                    'value': ['a', 'b'],
                    'props': {
                        'label.title': 'i18n:second_field:Second Field',
                        'multivalued': True,
                        'vocabulary': 'yafowil.yaml.tests.test_vocab'
                    },
                    'custom': {
                        'custom_stuff': {
                            'edit_renderers': 'context.custom_renderer',
                            'extractors': [
                                'context.custom_extractor_1',
                                'context.custom_extractor_2'
                            ]
                        }
                    }
                }
            }]
        })

    def test_yaml_parser(self):
        # Test YamlParser for yafowil forms
        # Write sane yaml template to tempdir
        template_path = os.path.join(self.tempdir, 'tmpl.yaml')
        with open(template_path, 'w') as file:
            file.write(self.yaml_tmpl)

        # Write broken yaml template to tempdir
        trash_path = os.path.join(self.tempdir, 'trash.yaml')
        with open(trash_path, 'w') as file:
            file.write("{]")

        # Create dummy context
        context = DummyContext()

        # Test inexistent yaml template path
        parser = YAMLParser('inexistent_path', context=context, message_factory=_)
        with self.assertRaises(YAMLTransformationError) as arc:
            parser()
        msg = "File not found: 'inexistent_path'"
        self.assertEqual(str(arc.exception), msg)

        # Test broken yaml template
        parser = YAMLParser(trash_path, context=context, message_factory=_)
        with self.assertRaises(YAMLTransformationError) as arc:
            parser()
        msg = "Cannot parse YAML from given path"
        self.assertTrue(str(arc.exception).startswith(msg))

        # Test with sane yaml template
        parser = YAMLParser(template_path, context=context, message_factory=_)
        self.assertTrue(parser.path.endswith('tmpl.yaml'))
        self.assertTrue(parser.context is context)

        # Parse definition values. If definition is a string
        ob = object()
        self.assertEqual(parser.parse_definition_value(ob), ob)
        self.assertEqual(parser.parse_definition_value('foo'), 'foo')

        self.assertEqual(
            parser.parse_definition_value('yafowil.yaml.tests.test_vocab')(None, None),
            test_vocab(None, None)
        )
        self.assertEqual(
            parser.parse_definition_value('context.firstfield_value'),
            context.firstfield_value
        )
        self.assertEqual(
            parser.parse_definition_value('context.new_style.old_style.test_method_2'),
            context.new_style.old_style.test_method_2
        )
        self.assertEqual(
            parser.parse_definition_value('context.NewStyle.old_style.test_method_2'),
            context.new_style.old_style.test_method_2
        )
        self.assertEqual(
            parser.parse_definition_value('context.NewStyle.OldStyle.test_method_2'),
            DummyContext.new_style.OldStyle.test_method_2
        )
        self.assertEqual(
            parser.parse_definition_value('yafowil.inexistent'),
            'yafowil.inexistent'
        )
        self.assertEqual(
            parser.parse_definition_value('context.inexistent'),
            'context.inexistent'
        )
        self.assertEqual(
            parser.parse_definition_value('inexistent.inexistent'),
            'inexistent.inexistent'
        )

        int_ = parser.parse_definition_value('python:int')
        self.assertTrue(int_ is int)
        with self.assertRaises(NameError) as arc:
            parser.parse_definition_value('python:UUID')
        self.assertEqual(str(arc.exception), "name 'UUID' is not defined")
        python_expression_globals['UUID'] = UUID
        UUID_ = parser.parse_definition_value('python:UUID')
        self.assertTrue(UUID_ is UUID)
        class CustomUUID(UUID):
            pass
        parser.expression_globals['UUID'] = CustomUUID
        UUID_ = parser.parse_definition_value('python:UUID')
        self.assertTrue(UUID_ is CustomUUID)

        fn = parser.parse_definition_value('expr:context.firstfield_value()')
        self.assertEqual(fn.__name__, 'fetch_value')
        self.assertEqual(fn.__module__, 'yafowil.yaml.parser')

        self.assertEqual(parser.parse_definition_value('i18n:foo'), 'foo')
        self.assertEqual(parser.parse_definition_value('i18n:foo:Foo'), 'Foo')
        with self.assertRaises(YAMLTransformationError) as arc:
            parser.parse_definition_value('i18n:foo:Foo:Fooo')
        self.assertEqual(str(arc.exception), 'to many : in i18n:foo:Foo:Fooo')

    def test_parse_from_yaml(self):
        template_path = os.path.join(self.tempdir, 'tmpl.yaml')
        with open(template_path, 'w') as file:
            file.write(self.yaml_tmpl)
        context = DummyContext()
        form = parse_from_YAML(template_path, context, _)
        self.assertEqual(form.treerepr().split('\n'), [
            "<class 'yafowil.base.Widget'>: demoform",
            "  <class 'yafowil.base.Widget'>: firstfield",
            "  <class 'yafowil.base.Widget'>: secondfield",
            ""
        ])
        self.assertEqual(sorted(form.attrs.items()), [('action', 'demoaction')])
        self.checkOutput("""
        <form action="demoaction" enctype="multipart/form-data"
              id="form-demoform" method="post" novalidate="novalidate">
          <div class="field" id="field-demoform-firstfield">
            <label for="input-demoform-firstfield">First Field</label>
            <input class="required text"
                data-flat="I am a flat data-attribute"
                data-i18n="i18n Nested First Field"
                data-nested="{&quot;nested-i18n&quot;: &quot;i18n Nested First Field&quot;}"
                id="input-demoform-firstfield"
                name="demoform.firstfield"
                required="required"
                type="text"
                value="First value"/>
          </div>
          <div class="field" id="field-demoform-secondfield">
            <label for="input-demoform-secondfield"
                   title="Second Field">secondfield</label>
            <input id="exists-demoform-secondfield"
                   name="demoform.secondfield-exists"
                   type="hidden" value="exists"/>
            <select class="select" id="input-demoform-secondfield"
                    multiple="multiple" name="demoform.secondfield">
              <option id="input-demoform-secondfield-a"
                      selected="selected" value="a">a</option>
              <option id="input-demoform-secondfield-b"
                      selected="selected" value="b">b</option>
              <option id="input-demoform-secondfield-c"
                      value="c">c</option>
            </select>
          </div>
        </form>
        """, fxml(form()))

    def test_yaml_form_flat(self):
        raw = """
            factory: form
            name: demoform
            props:
                action: demoaction
            widgets:
            - firstfield:
                factory: text
                value: context.some_attr
        """
        template_path = os.path.join(self.tempdir, 'tmpl.yaml')
        with open(template_path, 'w') as file:
            file.write(raw)
        context = DummyContext()
        form = YAMLParser(template_path, context=context)()
        self.checkOutput("""
        <form action="demoaction" enctype="multipart/form-data"
              id="form-demoform" method="post" novalidate="novalidate">
          <input class="text" id="input-demoform-firstfield"
                 name="demoform.firstfield" type="text"
                 value="context.some_attr"/>
        </form>
        """, fxml(form()))

    def test_yaml_form_compounds(self):
        raw = """
            factory: form
            name: demoform
            props:
                action: demoaction
            widgets:
            - sometable:
                factory: table
                props:
                    structural: True
                widgets:
                - row_1:
                    factory: tr
                    props:
                        structural: True
                    widgets:
                    - somefield:
                        factory: td:field:text
        """
        template_path = os.path.join(self.tempdir, 'tmpl.yaml')
        with open(template_path, 'w') as file:
            file.write(raw)
        context = DummyContext()
        form = YAMLParser(template_path, context=context)()
        self.checkOutput("""
        <form action="demoaction" enctype="multipart/form-data"
              id="form-demoform" method="post" novalidate="novalidate">
          <table>
            <tr>
              <td>
                <div class="field" id="field-demoform-somefield">
                  <input class="text" id="input-demoform-somefield"
                         name="demoform.somefield" type="text" value=""/>
                </div>
              </td>
            </tr>
          </table>
        </form>
        """, fxml(form()))

    yaml_main_tmpl = """
        factory: form
        name: mainform
        props:
            action: mainformaction
        widgets:
        - sub:
            nest: sub.yaml
    """

    def test_nested_form_single_field(self):
        # Create nested form, case single field
        main_path = os.path.join(self.tempdir, 'main.yaml')
        with open(main_path, 'w') as file:
            file.write(self.yaml_main_tmpl)
        nested_raw = """
            factory: text
            value: context.some_attr
            props:
                class_add: nested_input
        """
        nested_path = os.path.join(self.tempdir, 'sub.yaml')
        with open(nested_path, 'w') as file:
            file.write(nested_raw)
        context = DummyContext()
        form = YAMLParser(main_path, context=context)()
        self.checkOutput("""
        <form action="mainformaction" enctype="multipart/form-data"
              id="form-mainform" method="post" novalidate="novalidate">
          <input class="nested_input text" id="input-mainform-sub"
                 name="mainform.sub" type="text" value="context.some_attr"/>
        </form>
        """, fxml(form()))

    def test_nested_form_structural_compound(self):
        # Create nested form, case structural compound
        main_path = os.path.join(self.tempdir, 'main.yaml')
        with open(main_path, 'w') as file:
            file.write(self.yaml_main_tmpl)
        nested_raw = """
            factory: compound
            props:
                structural: True
            widgets:
            - subfieldname:
                factory: text
                value: subfieldvalue
        """
        nested_path = os.path.join(self.tempdir, 'sub.yaml')
        with open(nested_path, 'w') as file:
            file.write(nested_raw)
        context = DummyContext()
        form = YAMLParser(main_path, context=context)()
        self.checkOutput("""
        <form action="mainformaction" enctype="multipart/form-data"
              id="form-mainform" method="post" novalidate="novalidate">
          <input class="text" id="input-mainform-subfieldname"
                 name="mainform.subfieldname" type="text"
                 value="subfieldvalue"/>
        </form>
        """, fxml(form()))

    def test_nested_form_non_structural_compound(self):
        # Create nested form, case non structural compound
        main_path = os.path.join(self.tempdir, 'main.yaml')
        with open(main_path, 'w') as file:
            file.write(self.yaml_main_tmpl)
        nested_raw = """
            factory: compound
            widgets:
            - fieldname:
                factory: text
        """
        nested_path = os.path.join(self.tempdir, 'sub.yaml')
        with open(nested_path, 'w') as file:
            file.write(nested_raw)
        context = DummyContext()
        form = YAMLParser(main_path, context=context)()
        self.checkOutput("""
        <form action="mainformaction" enctype="multipart/form-data"
              id="form-mainform" method="post" novalidate="novalidate">
          <input class="text" id="input-mainform-sub-fieldname"
                 name="mainform.sub.fieldname" type="text" value=""/>
        </form>
        """, fxml(form()))

    def test_traceback_supplement(self):
        # Traceback supplement
        raw = """
            factory: form
            name: demoform
            props:
                action: demoaction
            widgets:
            - somefield:
                factory: td:field:text
                value: expr:context.fail_callback
        """
        template_path = os.path.join(self.tempdir, 'tmpl.yaml')
        with open(template_path, 'w') as file:
            file.write(raw)
        context = DummyContext()
        form = YAMLParser(template_path, context=context)()
        with self.assertRaises(ValueError):
            form()

    json_tmpl = """
        {
            "factory": "form",
            "name": "demoform",
            "props": {
                "action": "demoaction"
            },
            "widgets": [{
                "firstfield": {
                    "factory": "field:label:error:text",
                    "props": {
                        "description": "I am the description",
                        "label": "i18n:First Field",
                        "required": "I am required"
                    },
                    "value": "context.firstfield_value"
                }
            }, {
                "secondfield": {
                    "custom": {
                        "custom_stuff": {
                            "edit_renderers": "context.custom_renderer",
                            "extractors": [
                                "context.custom_extractor_1",
                                "context.custom_extractor_2"
                            ]
                        }
                    },
                    "factory": "field:label:*custom_stuff:error:select",
                    "props": {
                        "label.title": "i18n:second_field:Second Field",
                        "multivalued": true,
                        "vocabulary": "yafowil.yaml.tests.test_vocab"
                    },
                    "value": [
                        "a",
                        "b"
                    ]
                }
            }]
        }
    """

    def test_parse_from_json(self):
        # Check if json works too
        json_file = os.path.join(self.tempdir, 'test.json')
        with open(json_file, 'w') as file:
            file.write(self.json_tmpl)
        context = DummyContext()
        form = YAMLParser(json_file, context=context, message_factory=_)()
        self.assertEqual(form.treerepr().split('\n'), [
            "<class 'yafowil.base.Widget'>: demoform",
            "  <class 'yafowil.base.Widget'>: firstfield",
            "  <class 'yafowil.base.Widget'>: secondfield",
            ""
        ])
        trash_file = os.path.join(self.tempdir, 'trash.json')
        with open(trash_file, 'w') as file:
            file.write("{]")
        parser = YAMLParser(trash_file, context=context, message_factory=_)
        with self.assertRaises(JSONTransformationError) as arc:
            parser()
        msg = 'Cannot parse JSON from given path'
        self.assertTrue(str(arc.exception).startswith(msg))
        nonexisting_file = os.path.join(self.tempdir, 'nonexisting.json')
        parser = YAMLParser(nonexisting_file, context=context, message_factory=_)
        with self.assertRaises(JSONTransformationError) as arc:
            parser()
        msg = 'File not found'
        self.assertTrue(str(arc.exception).startswith(msg))


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(
        unittest.TestLoader().loadTestsFromTestCase(TestYAML)
    )
    suite.addTest(
        doctest.DocFileSuite(
            'sphinx.rst',
            optionflags=(
                doctest.NORMALIZE_WHITESPACE |
                doctest.ELLIPSIS |
                doctest.REPORT_ONLY_FIRST_FAILURE
            ),
            globs={
                'pxml': pxml
            }
        )
    )
    return suite


if __name__ == '__main__':
    from yafowil.yaml import tests
    unittest.main(defaultTest='test_suite')                  # pragma: no cover

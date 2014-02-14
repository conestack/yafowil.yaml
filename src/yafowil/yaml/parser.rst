Sample form definition::

    >>> raw = """
    ... factory: form
    ... name: demoform
    ... props:
    ...     action: demoaction
    ... widgets:
    ... - firstfield:
    ...     factory: field:label:error:text
    ...     value: context.firstfield_value
    ...     props:
    ...         label: i18n:First Field
    ...         description: I am the description
    ...         required: I am required
    ... - secondfield:
    ...     factory: field:label:*custom_stuff:error:select
    ...     value: ['a', 'b']
    ...     props:
    ...         label.title: i18n:second_field:Second Field
    ...         multivalued: True
    ...         vocabulary: yafowil.yaml.tests.test_vocab
    ...     custom:
    ...         custom_stuff:
    ...             extractors:
    ...                 - context.custom_extractor_1
    ...                 - context.custom_extractor_2
    ...             edit_renderers: context.custom_renderer
    ... """

Check how yaml parses this::

    >>> import yaml
    >>> pprint(yaml.load(raw))
    {'factory': 'form',
     'name': 'demoform',
     'props': {'action': 'demoaction'},
     'widgets': [{'firstfield': {'factory': 'field:label:error:text',
                                 'props': {'description': 'I am the description',
                                           'label': 'i18n:First Field',
                                           'required': 'I am required'},
                                 'value': 'context.firstfield_value'}},
                 {'secondfield': {'custom': {'custom_stuff': {'edit_renderers': 'context.custom_renderer',
                                                              'extractors': ['context.custom_extractor_1',
                                                                             'context.custom_extractor_2']}},
                                  'factory': 'field:label:*custom_stuff:error:select',
                                  'props': {'label.title': 'i18n:second_field:Second Field',
                                            'multivalued': True,
                                            'vocabulary': 'yafowil.yaml.tests.test_vocab'},
                                  'value': ['a', 'b']}}]}

Create tmp env::

    >>> import os
    >>> import tempfile
    >>> tempdir = tempfile.mkdtemp()
    >>> template_path = os.path.join(tempdir, 'tmpl.yaml')
    >>> with open(template_path, 'w') as file:
    ...     file.write(raw)

    >>> trash_path = os.path.join(tempdir, 'trash.yaml')
    >>> with open(trash_path, 'w') as file:
    ...     file.write("{]")

Create dummy context::

    >>> class DummyContext(object):
    ...     some_attr = ''
    ...     @property
    ...     def fail_callback(self):
    ...         raise ValueError('I am supposed to fail')
    ...     def firstfield_value(self, widget, data):
    ...         return 'First value'
    ...     def custom_extractor_1(self, widget, data):
    ...         return data.extracted
    ...     def custom_extractor_2(self, widget, data):
    ...         return data.extracted
    ...     def custom_renderer(self, widget, data):
    ...         return data.rendered
    ...     class NewStyle(object):
    ...         class Another(object):
    ...             def test_method_1(self, widget, data):
    ...                 return 'Test method 1'
    ...         class OldStyle:
    ...             def test_method_2(self, widget, data):
    ...                 return 'Test method 2'
    ...         old_style = OldStyle()
    ...     new_style = NewStyle()

    >>> context = DummyContext()

Dummy message factory::

    >>> _ = lambda x, default=None: default and default or x

Test YamlParser for yafowil forms::

    >>> from yafowil.yaml import YAMLParser

    >>> YAMLParser('inexistent_path', context=context, message_factory=_)()
    Traceback (most recent call last):
      ...
    YAMLTransformationError: File not found: 'inexistent_path'

    >>> YAMLParser(trash_path, context=context, message_factory=_)()
    Traceback (most recent call last):
      ...
    YAMLTransformationError: Cannot parse YAML from given path
    '...trash.yaml'. Original exception was: ...

    >>> parser = YAMLParser(template_path, context=context, message_factory=_)
    >>> parser
    <yafowil.yaml.parser.YAMLParser object at ...>

    >>> parser.path
    '...tmpl.yaml'

    >>> parser.context
    <DummyContext object at ...>

Parse definition values. If definition is a string::

    >>> parser.parse_definition_value(object())
    <object object at ...>

    >>> parser.parse_definition_value('foo')
    'foo'

    >>> parser.parse_definition_value('yafowil.yaml.tests.test_vocab')
    <function test_vocab at ...>

    >>> parser.parse_definition_value('context.firstfield_value')
    <bound method DummyContext.firstfield_value of <DummyContext object at ...>>

    >>> parser.parse_definition_value('context.new_style.old_style.test_method_2')
    <bound method OldStyle.test_method_2 of <__builtin__.OldStyle instance at
    ...>>

    >>> parser.parse_definition_value('context.NewStyle.old_style.test_method_2')
    <bound method OldStyle.test_method_2 of <__builtin__.OldStyle instance at
    ...>>

    >>> parser.parse_definition_value('context.NewStyle.OldStyle.test_method_2')
    <unbound method OldStyle.test_method_2>

    >>> parser.parse_definition_value('yafowil.inexistent')
    'yafowil.inexistent'

    >>> parser.parse_definition_value('context.inexistent')
    'context.inexistent'

    >>> parser.parse_definition_value('inexistent.inexistent')
    'inexistent.inexistent'

    >>> parser.parse_definition_value('expr:context.firstfield_value()')
    <function fetch_value at ...>

    >>> from yafowil.yaml import parse_from_YAML
    >>> form = parse_from_YAML(template_path, context, _)
    >>> form
    <Widget object 'demoform' at ...>

    >>> form.printtree()
    <class 'yafowil.base.Widget'>: demoform
      <class 'yafowil.base.Widget'>: firstfield
      <class 'yafowil.base.Widget'>: secondfield

    >>> form.attrs.items()
    [('action', 'demoaction')]

    >>> pxml(form())
    <form action="demoaction" enctype="multipart/form-data" id="form-demoform" method="post" novalidate="novalidate">
      <div class="field" id="field-demoform-firstfield">
        <label for="input-demoform-firstfield">First Field</label>
        <input class="required text" id="input-demoform-firstfield" name="demoform.firstfield" required="required" type="text" value="First value"/>
      </div>
      <div class="field" id="field-demoform-secondfield">
        <label for="input-demoform-secondfield" title="Second Field">secondfield</label>
        <input id="exists-demoform-secondfield" name="demoform.secondfield-exists" type="hidden" value="exists"/>
        <select class="select" id="input-demoform-secondfield" multiple="multiple" name="demoform.secondfield">
          <option id="input-demoform-secondfield-a" selected="selected" value="a">a</option>
          <option id="input-demoform-secondfield-b" selected="selected" value="b">b</option>
          <option id="input-demoform-secondfield-c" value="c">c</option>
        </select>
      </div>
    </form>
    <BLANKLINE>

    >>> raw = """
    ... factory: form
    ... name: demoform
    ... props:
    ...     action: demoaction
    ... widgets:
    ... - firstfield:
    ...     factory: text
    ...     value: context.some_attr
    ... """

    >>> template_path = os.path.join(tempdir, 'tmpl.yaml')
    >>> with open(template_path, 'w') as file:
    ...     file.write(raw)

    >>> form = YAMLParser(template_path, context=context)()
    >>> pxml(form())
    <form action="demoaction" enctype="multipart/form-data" id="form-demoform" method="post" novalidate="novalidate">
      <input class="text" id="input-demoform-firstfield" name="demoform.firstfield" type="text" value="context.some_attr"/>
    </form>
    <BLANKLINE>

    >>> raw = """
    ... factory: form
    ... name: demoform
    ... props:
    ...     action: demoaction
    ... widgets:
    ... - sometable:
    ...     factory: table
    ...     props:
    ...         structural: True
    ...     widgets:
    ...     - row_1:
    ...         factory: tr
    ...         props:
    ...             structural: True
    ...         widgets:
    ...         - somefield:
    ...             factory: td:field:text
    ... """

    >>> template_path = os.path.join(tempdir, 'tmpl.yaml')
    >>> with open(template_path, 'w') as file:
    ...     file.write(raw)

    >>> form = YAMLParser(template_path, context=context)()
    >>> pxml(form())
    <form action="demoaction" enctype="multipart/form-data" id="form-demoform" method="post" novalidate="novalidate">
      <table>
        <tr>
          <td>
            <div class="field" id="field-demoform-somefield">
              <input class="text" id="input-demoform-somefield" name="demoform.somefield" type="text" value=""/>
            </div>
          </td>
        </tr>
      </table>
    </form>
    <BLANKLINE>

Traceback supplement::

    >>> raw = """
    ... factory: form
    ... name: demoform
    ... props:
    ...     action: demoaction
    ... widgets:
    ... - somefield:
    ...     factory: td:field:text
    ...     value: expr:context.fail_callback
    ... """

    >>> template_path = os.path.join(tempdir, 'tmpl.yaml')
    >>> with open(template_path, 'w') as file:
    ...     file.write(raw)

    >>> form = YAMLParser(template_path, context=context)()
    >>> pxml(form())
    Traceback (most recent call last):
      ...
        data.rendered = renderer(self, data)
        yafowil widget processing info:
        - path      : demoform
        - blueprints: ['form']
        - task      : render
        - descr     : failed at 'form' in mode 'edit'
      File ...
        data.value = self.getter(self, data)
        yafowil widget processing info:
        - path      : demoform.somefield
        - blueprints: ['td', 'field', 'text']
        - task      : run preprocessors
        - descr     : execute
      ...
    ValueError: I am supposed to fail

Cleanup::

    >>> import shutil
    >>> shutil.rmtree(tempdir)

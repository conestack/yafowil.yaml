It is possible to describe YAFOWIL forms using `YAML <http://www.yaml.org/>`_
as description language.

`JSON <http://www.json.org/JSON>`_ syntax is a
`subset <https://en.wikipedia.org/wiki/YAML#JSON>`_ of YAML version 1.2, so we
support JSON too.


Create file containing form description
---------------------------------------

Create a file, i.e. ``demo_form.yaml`` and add widget configuration.

.. code-block:: yaml

    factory: form
    name: demo_form
    props:
        action: context.form_action
    widgets:
    - title:
        factory: "label:field:error:text"
        value: expr:context.get('title', '')
        props:
            label: i18n:title:Title
            required: i18n:title_required:No title given
    - description:
        factory: label:field:textarea
        value: expr:context.get('description', '')
        props:
            label: i18n:description:Description
            rows: 5
    - save:
        factory: submit
        props:
            action: save
            expression: True
            handler: context.save
            next: context.next
            label: i18n:save:Save

In JSON notation the same would look like this.

.. code-block:: json

    {
      "factory": "form",
      "name": "demo_form",
      "props": {
        "action": "context.form_action"
      },
      "widgets": [
        {
          "title": {
            "factory": "label:field:error:text",
            "value": "expr:context.get('title', '')",
            "props": {
              "label": "i18n:title:Title",
              "required": "i18n:title_required:No title given"
            }
          }
        },
        {
          "description": {
            "factory": "label:field:textarea",
            "value": "expr:context.get('description', '')",
            "props": {
              "label": "i18n:description:Description",
              "rows": 5
            }
          }
        },
        {
          "save": {
            "factory": "submit",
            "props": {
              "action": "save",
              "expression": true,
              "handler": "context.save",
              "label": "i18n:save:Save",
              "next": "context.next"
            }
          }
        }
      ]
    }

Each widget node is represented by an associative array.
Keys are mapping to corresponding arguments of ``yafowil.base.factory``
signature:

``factory``
    Chained factory registration names.

``name``
    Widget name. Only required on root, for children widget key is used.

``value``
    Widget value or callable/expression returning widget value.

``props``
    Widget properties as associative array.
    You can prefix individual properties with the name of the blueprint to
    address a specific blueprint.
    For Example use: label.title to set the title attribute of the label.

``custom``
    Custom widget properties as associative array.

``mode``
    Widget rendering mode or callable/expression returning widget rendering
    mode.

``nest``
    Include other yaml/json file representing this widget.

``widgets``
    Child widgets as list. Each child widget is an associative array with one
    key - the widget name - containing again an associative array with the keys
    descibed here.


Computed values
---------------

Beside static values, definitions may contain python expressions, i18n message
strings, access to a rendering context and pointers to callables.

``i18n:``
    If definition value starts with ``i18n:``, a message string gets created
    by calling given message factory.

``expr:``
    If definition value starts with ``expr:``, a yafowil callback wrapper gets
    created, accepting ``widget`` and ``data`` keyword arguments, which is
    executed when the widget tree is processed. For security reasons, only
    rendering ``context``, ``widget`` and ``data`` are available
    in expressions.

``python:``
    If definition value starts with ``python:`` it gets evaluated as plain
    python expression. This is useful for the rare cases where yafowil or one
    of it's addons expects a callable not accepting ``widget`` and ``data``
    as arguments, like ``datatype`` does. By default, these expressions get an
    empty globals dictionary. Python expression globals can be customized
    either globally by adding values to ``yafowil.yaml.python_expression_globals``
    or per parser run by passing ``expression_globals`` to ``YAMLParser``
    constructor respective ``parse_from_YAML`` function. Parser specific globals
    take precedence over globally defined ones.

``context``
    If definition value starts with ``context``, rendering context is used to
    lookup callbacks. If lookup fails, return definition value as string.

``.`` in value
    If ``.`` is found in value string, try to lookup callback from module path.
    When lookup fails, return definition value as string.


Define rendering context
------------------------

A rendering context has to be provided. Refering to the form description
example above, this may look like:

.. code-block:: pycon

    >>> class FormRenderingContext(object):
    ...
    ...     def get(self, key, default=None):
    ...         # do data lookup here
    ...         value = key
    ...         return value
    ...
    ...     def form_action(self, widget, data):
    ...         # create and return form action URL
    ...         return 'http://example.com/form_action'
    ...
    ...     def save(self, widget, data):
    ...         # extract and save form data
    ...         pass
    ...
    ...     def next(self, request):
    ...         # compute and return next URL
    ...         return 'http://example.com/form_action_succeed'


Create Message Factory
----------------------

Unless no others are registered one want to use message factories from
``pyramid.i18n`` or ``zope.i18nmessageid``. See refering documentation for
details. Here we create a dummy message factory:

.. code-block:: pycon

    >>> message_factory = lambda x: x


Creating YAFOWIL-Forms form YAML-Files
--------------------------------------

To create a yafowil widget tree from YAML, use ``yafowil.yaml.parse_from_YAML``.
This accepts also JSON file files ending with ``.json``.
To adress a specific pyhton package path prefix the filename with
``my.module:``:

.. code-block:: pycon

    >>> import yafowil.loader
    >>> from yafowil.yaml import parse_from_YAML

    >>> rendering_context = FormRenderingContext()
    >>> expression_globals = {}
    >>> form = parse_from_YAML(
    ...     'yafowil.yaml:demo_form.yaml',
    ...     context=rendering_context,
    ...     message_factory=message_factory,
    ...     expression_globals=expression_globals
    ... )

This results into...::

    >>> form.printtree()
    <class 'yafowil.base.Widget'>: demo_form
      <class 'yafowil.base.Widget'>: title
      <class 'yafowil.base.Widget'>: description
      <class 'yafowil.base.Widget'>: save

...which renders::

    >>> pxml(form())
    <form action="http://example.com/form_action" enctype="multipart/form-data" id="form-demo_form" method="post" novalidate="novalidate">
      <label class="form-label required" for="input-demo_form-title">Title</label>
      <div class="field" id="field-demo_form-title">
        <input class="form-control required" id="input-demo_form-title" name="demo_form.title" required="required" type="text" value="title"/>
      </div>
      <label class="form-label" for="input-demo_form-description">Description</label>
      <div class="field" id="field-demo_form-description">
        <textarea class="form-control" cols="80" id="input-demo_form-description" name="demo_form.description" rows="5">description</textarea>
      </div>
      <input class="btn btn-primary mb-3 text-light" id="input-demo_form-save" name="action.demo_form.save" type="submit" value="Save"/>
    </form>
    <BLANKLINE>


Manage translations of YAML forms
---------------------------------

As shown above, YAML forms may contain i18n translation strings. The message
strings and the corresponding default values can be extracted automatically
and written to po files using `lingua <http://pypi.python.org/pypi/lingua>`_
if `yafowil.lingua <http://pypi.python.org/pypi/yafowil.lingua>`_ plugin is
installed.

For details on managing translations with ``lingua`` please refer to
corresponding documentation.


Usage
=====


Create YAML file containing form description
--------------------------------------------

::

    factory: form
    name: demo_form
    props:
        action: context.form_action
    widgets:
    - title:
        factory: label:field:error:text
        value: expr:context.get('title', '')
        props:
            label: i18n:Title
            required: No title given
    - description:
        factory: label:field:textarea
        value: expr:context.get('description', '')
        props:
            label: i18n:Description
            rows: 5
    - save:
        factory: submit
        props:
            action: save
            expression: True
            handler: context.save
            next: context.next
            label: i18n:Save


Each widget node is represented by an associative array. Keys are mapping to
corresponding arguments of ``yafowil.base.factory`` signature: 

``factory``
    Chained factory registration names.

``name``
    Widget name. Only required on root, for children widget key is used.

``value``
    Widget value or callable/expression returning widget value.

``props``
    Widget properties as associative array.

``custom``
    Custom widget properties as associative array.

``widgets``
    Child widgets as list. Each child widget is an associative array with one
    key - the widget name - containing again an associative array with the keys
    descibed here.


Resolution of definition values
-------------------------------

Beside static values, definitions may contain python expressions, i18n message 
strings, access to a rendering context and pointers to callables.

- If definition value starts with ``i18n:``, a message string gets created
  by calling given message factory.

- If definition value starts with ``expr:``, a callback wrapper is created
  which gets executed each time the widget tree gets rendered. For security
  reasons, only rendering context is accessible in expressions.

- If definition value starts with ``context``, rendering context is used to
  lookup callbacks. If lookup fails, return definition value as string.

- If '.' is found in definition value, try to lookup callback from module path.
  If lookup fails, return definition value as string.


Define rendering context
------------------------

A rendering context is provided by a class. Refering to the form description
example above, this looks like::

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

Usually someone uses message factories from ``pyramid.i18n`` or 
``zope.i18nmessageid``. See refering documentation for details.

    >>> message_factory = lambda x: x


Obtaining YAML Forms
--------------------

To obtain a yafowil widget tree from YAML, use
``yafowil.yaml.parse_from_YAML``::

    >>> import yafowil.loader
    >>> from yafowil.yaml import parse_from_YAML
    
    >>> rendering_context = FormRenderingContext()
    >>> form = parse_from_YAML(demo_form_path,
    ...                        context=rendering_context,
    ...                        message_factory=message_factory)

This results to...::
    
    >>> form.printtree()
    <class 'yafowil.base.Widget'>: demo_form
      <class 'yafowil.base.Widget'>: title
      <class 'yafowil.base.Widget'>: description
      <class 'yafowil.base.Widget'>: save

...which renders::

    >>> pxml(form())
    <form action="http://example.com/form_action" enctype="multipart/form-data" id="form-demo_form" method="post" novalidate="novalidate">
      <label for="input-demo_form-title">Title</label>
      <div class="field" id="field-demo_form-title">
        <input class="required text" id="input-demo_form-title" name="demo_form.title" required="required" type="text" value="title"/>
      </div>
      <label for="input-demo_form-description">Description</label>
      <div class="field" id="field-demo_form-description">
        <textarea cols="80" id="input-demo_form-description" name="demo_form.description" rows="5">description</textarea>
      </div>
      <input id="input-demo_form-save" name="action.demo_form.save" type="submit" value="Save"/>
    </form>
    <BLANKLINE>

Changes
=======

3.0.0 (unreleased)
------------------

- Refactor package layout to use ``pyproject.toml`` and implicit namespace packages.
  [rnix]


2.1 (2025-10-28)
----------------

- Pin upper versions of dependencies.
  [rnix]

- Switch from buildout to mxmake.
  [rnix]


2.0 (2022-12-05)
----------------

- Fix parsing of ``builders`` and ``display_renderers`` in custom parts.
  [rnix]

- Fix signature of ``yafowil.yaml.tests.test_vocab``. Property callbacks always
  gets passed ``widget`` and ``data`` as of yafowil 3.0.0.
  [rnix]

- Parse values of attributes (data-Attributes) if type() is dict.
  HTML5 Data-Attributes with i18n or callables are possible now.
  [2silver]

**Breaking changes:**

- Add ``python:`` expressions. Needed for cases where property callbacks not
  accept ``widget`` and ``data`` keyword arguments, e.g. ``datatype``. This is
  necessary because ``callable_value`` function in yafowil 3.0 no longer calls
  callable without arguments as fallback.
  [rnix]


1.3.1 (2020-07-09)
------------------

- Pass ``yaml.SafeLoader`` loader to ``yaml.load`` to prevent arbitrary code
  execution.
  [rnix]

- Cleanup.
  [rnix]


1.3 (2018-07-16)
----------------

- Python 3 compatibility.
  [rnix]

- Convert doctests to unittests.
  [rnix]


1.2 (2014-11-13)
----------------

- Feature: Support definitions written in JSON too. Since YAML and JSON are
  100% comaptible exact the same structure applies.
  [jensens, 2014-11-13]

1.1
---

- Widget definitions in yaml may point to other yaml files for form nesting
  using ``nest`` property.
  [rnix, 2014-07-18]

1.0.5
-----

- Fix test coverage.
  [rnix, jensens, 2014-04-30]

1.0.4
-----

- allow default for i18n messages in format:
  ``i18n:message_id:Default Value``
  [rnix, jensens, 2014-02-14]

1.0.3
-----

- test coverage, documentation
  [rnix, jensens]

1.0.2
-----

- accidentially set zip_safe=True which is not. Set to Fasle now.
  [jensens, 2012-03-19]

1.0.1
-----

- Adopt test for ``select`` blueprint change.
  [rnix, 2011-12-18]

- Fix automatic name setting for recursive compounds.
  [rnix, 2011-09-30]

1.0
---

- Adopt to yafowil 1.1.
  [rnix, 2011-07-07]

- Extend ``parse_from_YAML`` resolving package path instead of excepting.
  absolute or relative file path
  [rnix, 2011-07-07]

0.9.1
-----

- Add i18n support.
  [rnix, 2011-06-04]

- Fix bug where expression evaluation was not reached.
  [rnix, 2011-06-04]

- Adopt tests for form novalidate property.
  [rnix, 2011-05-23]

0.9
---

- Make it work.
  [aatis, rnix]

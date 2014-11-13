# -*- coding: utf-8 -*-
from interlude import interact
from pprint import pprint
import doctest
import lxml.etree as etree
import unittest

optionflags = (
    doctest.NORMALIZE_WHITESPACE |
    doctest.ELLIPSIS |
    doctest.REPORT_ONLY_FIRST_FAILURE
)
TESTFILES = [
    'parser.rst',
    'sphinx.rst',
]


def test_vocab():
    """Used by tests to determine package path
    """
    return ['a', 'b', 'c']


def fxml(xml):
    et = etree.fromstring(xml)
    return etree.tostring(et, pretty_print=True)


def pxml(xml):
    print fxml(xml)


def test_suite():
    return unittest.TestSuite([
        doctest.DocFileSuite(
            file,
            optionflags=optionflags,
            globs={'interact': interact,
                   'pprint': pprint,
                   'pxml': pxml},
        ) for file in TESTFILES
    ])

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')                # pragma NO COVERAGE

# -*- coding: utf-8 -*-
from setuptools import find_packages
from setuptools import setup
import os


version = '1.3'
shortdesc = 'YAFOWIL - YAML-/ JSON-parser for widget trees.'
longdesc = open(os.path.join(os.path.dirname(__file__), 'README.rst')).read()
longdesc += open(os.path.join(os.path.dirname(__file__), 'HISTORY.rst')).read()
longdesc += open(os.path.join(os.path.dirname(__file__), 'LICENSE.rst')).read()
tests_require = ['yafowil[test]']


setup(
    name='yafowil.yaml',
    version=version,
    description=shortdesc,
    long_description=longdesc,
    classifiers=[
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Software Development',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
    ],
    keywords='html input widgets form compound',
    author='BlueDynamics Alliance',
    author_email='dev@bluedynamics.com',
    url=u'http://pypi.python.org/pypi/yafowil.yaml',
    license='BSD',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    namespace_packages=['yafowil'],
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'setuptools',
        'yafowil>1.0.4',
        'PyYAML',
    ],
    tests_require=tests_require,
    test_suite="yafowil.yaml.tests.test_suite",
    extras_require=dict(
        test=tests_require,
    ))

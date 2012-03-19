from setuptools import setup, find_packages
import os

version = '1.0.1'
shortdesc = \
'YAFOWIL - YAML parser for widget trees.'
longdesc = open(os.path.join(os.path.dirname(__file__), 'README.rst')).read()
longdesc += open(os.path.join(os.path.dirname(__file__), 'HISTORY.rst')).read()
longdesc += open(os.path.join(os.path.dirname(__file__), 'LICENSE.rst')).read()
tests_require = [
    'interlude',
    'lxml',
    'yafowil>1.0.4',
    'PyYAML',
]

setup(name='yafowil.yaml',
      version=version,
      description=shortdesc,
      long_description=longdesc,
      classifiers=[
            'Operating System :: OS Independent',
            'Programming Language :: Python',
            'Topic :: Software Development',
            'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
            'License :: OSI Approved :: BSD License',
      ],
      keywords='html input widgets form compound',
      author='BlueDynamics Alliance',
      author_email='dev@bluedynamics.com',
      url=u'',
      license='Simplified BSD',
      packages=find_packages('src'),
      package_dir = {'': 'src'},
      namespace_packages=['yafowil'],
      include_package_data=True,
      zip_safe=True,
      install_requires=[
          'setuptools',
          'yafowil>1.0.4',
          'PyYAML',
      ],
      tests_require=tests_require,
      test_suite="yafowil.yaml.tests.test_suite",
      extras_require = dict(
          test=tests_require,
      ),
)

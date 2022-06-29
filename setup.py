# Copyright (c) str4d <str4d@mail.i2p>
# See COPYING for details.

from setuptools import setup
from os import path
import sys


here = path.abspath(path.dirname(__file__))

def readme():
    with open(path.join(here, 'README.rst')) as f:
        return f.read()

install_requires = [
    'Parsley>=1.2',
]

# future is only a requirement for Py2
# This will not work on Py3 if any of the 14 standard library modules listed
# here get used later on:
# http://python-future.org/standard_library_imports.html#list-standard-library-refactored
if sys.version_info[0] < 3:
    install_requires.append('future>=0.14.0')
    install_requires.append('Twisted>=10.1')
else:
    install_requires.append('Twisted>=15.4')

setup(
    name='txi2p-tahoe',
    description='I2P bindings for Twisted',
    long_description=readme(),
    author='str4d',
    author_email='str4d@i2pmail.org',
    url='https://github.com/str4d/txi2p',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Framework :: Twisted',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: ISC License (ISCL)',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Topic :: Internet',
    ],
    license='ISC',
    install_requires=install_requires,
    packages=[
        'txi2p',
        'txi2p.bob',
        'txi2p.sam',
        'txi2p.test',
        'txi2p.bob.test',
        'txi2p.sam.test',
        'twisted.plugins',
    ],
    extras_require={
        "test": [
            "mock; python_version < '3.0'",
        ],
    },
)

# Make Twisted regenerate the dropin.cache, if possible.  This is necessary
# because in a site-wide install, dropin.cache cannot be rewritten by
# normal users.
try:
    from twisted.plugin import IPlugin, getPlugins
except ImportError:
    pass
else:
    list(getPlugins(IPlugin))

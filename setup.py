# Copyright (c) str4d <str4d@mail.i2p>
# See COPYING for details.

from setuptools import setup
from os import path


here = path.abspath(path.dirname(__file__))

def readme():
    with open(path.join(here, 'README.rst')) as f:
        return f.read()

setup(
    name='txi2p',
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
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.4',
        'Topic :: Internet',
    ],
    license='ISC',

    # This is left to support installation with pip < 10 or with another tool.
    # However, it is expected that modern installations will be performed with
    # pip >= 10 and will look at pyproject.toml first, mooting this
    # declaration.
    setup_requires=['vcversioner>=1'],
    vcversioner={
        'version_module_paths': ['txi2p/_version.py'],
    },
    install_requires=[
        'Twisted>=10.1',
        'Parsley>=1.2',
    ],
    packages=[
        'txi2p',
        'txi2p.bob',
        'txi2p.sam',
        'txi2p.test',
        'txi2p.bob.test',
        'txi2p.sam.test',
        'twisted.plugins',
    ],
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

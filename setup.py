# Copyright (c) str4d <str4d@mail.i2p>
# See COPYING for details.

from setuptools import setup


with open('README.rst', 'rb') as infile:
    long_description = infile.read()

with open('requirements.txt', 'rb') as infile:
    install_requires = infile.read().split()

setup(
    name='txi2p',
    description='I2P bindings for Twisted',
    long_description=long_description,
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
        'Programming Language :: Python :: 2 :: Only',
        'Topic :: Internet',
    ],
    license='ISC',

    setup_requires=['vcversioner>=1'],
    vcversioner={
        'version_module_paths': ['txi2p/_version.py'],
    },
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

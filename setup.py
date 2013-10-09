# Copyright (c) str4d <str4d@mail.i2p>
# See COPYING for details.

from distutils.core import setup

with open('requirements.txt', 'rb') as infile:
    install_requires = infile.read().split()

setup(
    name='txi2p',
    description='I2P bindings for Twisted.',
    author='str4d',
    author_email='str4d@mail.i2p',
    url='https://github.com/str4d/txi2p',
    license='ISC',
    install_requires=install_requires,
    packages=['txi2p', 'txi2p.test'] + ['twisted.plugins'],
    version='0.0.1',
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

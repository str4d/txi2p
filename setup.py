# Copyright (c) str4d <str4d@mail.i2p>
# See COPYING for details.

from distutils.core import setup

setup(
    name='i2p_twisted',
    description='I2P integration with Twisted.',
    author='str4d',
    author_email='str4d@mail.i2p',
    url='https://github.com/str4d/twisted-i2p',
    license='ISC',
    packages=['i2p.twisted', 'i2p.twisted.test'] + ['twisted.plugins'],
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

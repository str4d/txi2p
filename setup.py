from distutils.core import setup

PROJECT = 'i2p_twisted'
setup(
    name=PROJECT,
    packages=['i2p.twisted'] + ['twisted.plugins'],
    version='0.0.1',

    # url='',
    author='str4d',
    author_email='str4d@mail.i2p',
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

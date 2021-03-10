===========
txi2p-tahoe
===========

This is a hopefully temporary fork of txi2p_, to help Tahoe-LAFS_
project to get unstuck in Python 3 porting efforts.

.. _txi2p: https://pypi.org/project/txi2p/
.. _Tahoe-LAFS: https://pypi.org/project/tahoe-lafs/

.. image:: https://api.travis-ci.org/str4d/txi2p.svg?branch=master
    :target: https://www.travis-ci.org/str4d/txi2p
    :alt: travis

.. image:: https://coveralls.io/repos/github/str4d/txi2p/badge.svg?branch=master
    :target: https://coveralls.io/github/str4d/txi2p?branch=master
    :alt: coveralls

|txi2p| is a set of I2P bindings for `Twisted <https://twistedmatrix.com/>`_
10.1 or greater. It currently requires Python 2.

|txi2p| will run on Python 3.3+ (requiring `Twisted`_ 15.4 or greater).

|txi2p| supports both the SAM and BOB APIs for I2P. The default API is SAM.

Installation
============

You can install |txi2p| from PyPI::

    $ pip install txi2p-tahoe

or by downloading the source and running::

    $ pip install .

inside the source directory.

Quickstart
==========

If you are not familiar with using endpoints or endpoint strings, read the
`Twisted endpoints`_ documentation.

.. _Twisted endpoints: https://twistedmatrix.com/documents/current/core/howto/endpoints.html

Using endpoint classes
----------------------

To connect to an I2P site::

    from twisted.internet import reactor
    from twisted.internet.endpoints import clientFromString
    from txi2p.sam import SAMI2PStreamClientEndpoint

    samEndpoint = clientFromString(reactor, 'tcp:127.0.0.1:7656')
    endpoint = SAMI2PStreamClientEndpoint.new(samEndpoint, 'stats.i2p')
    d = endpoint.connect(factory)

To have a server listen on an I2P Destination::

    from twisted.internet import reactor
    from twisted.internet.endpoints import clientFromString
    from txi2p.sam import SAMI2PStreamServerEndpoint

    samEndpoint = clientFromString(reactor, 'tcp:127.0.0.1:7656')
    endpoint = SAMI2PStreamServerEndpoint.new(samEndpoint, '/path/to/keyfile')
    d = endpoint.listen(factory)

Using endpoint strings
----------------------

Requires `Twisted`_ 14.0 or greater.

To connect to an I2P site::

    from twisted.internet import reactor
    from twisted.internet.endpoints import clientFromString

    endpoint = clientFromString(reactor, 'i2p:stats.i2p')
    d = endpoint.connect(factory)

To have a server listen on an I2P Destination::

    from twisted.internet import reactor
    from twisted.internet.endpoints import serverFromString

    endpoint = serverFromString(reactor, 'i2p:/path/to/keyfile')
    d = endpoint.listen(factory)

To connect using a specific API::

    from twisted.internet import reactor
    from twisted.internet.endpoints import clientFromString

    endpoint = clientFromString(reactor, 'i2p:stats.i2p:api=BOB')
    d = endpoint.connect(factory)

To connect using a non-standard API host or port::

    from twisted.internet import reactor
    from twisted.internet.endpoints import clientFromString

    endpoint = clientFromString(reactor, 'i2p:stats.i2p:api=SAM:apiEndpoint=tcp\:127.0.0.1\:31337')
    d = endpoint.connect(factory)


Endpoint strings
================

The Twisted plugin for |clientFromString| and |serverFromString| will
only work for `Twisted`_ 14.0 or greater.

Both client and server strings support the following keyword arguments:

* ``api=<apiName>`` - Either ``SAM`` or ``BOB``.
* ``apiEndpoint=<endpointString>`` - An escaped client endpoint string pointing
  to the API, e.g. ``tcp\:127.0.0.1\:2827``.
* ``options=keyOne\:valueOne,keyTwo\:valueTwo`` - I2CP options as a
  comma-separated key:value list. See the `I2CP specification` for available
  options.

.. _I2CP specification: https://geti2p.net/en/docs/protocol/i2cp

Clients
-------

Client string format::

    i2p:<host>[:port][:key=value]*

Supported arguments:

**SAM**

* ``nickname``
* ``autoClose``
* ``keyfile``
* ``localPort``
* ``sigType``

**BOB**

* ``tunnelNick``
* ``inhost``
* ``inport``

Servers
-------

Server string format::

    i2p:<keyfile>[:port][:key=value]*

Supported arguments:

**SAM**

* ``nickname``
* ``autoClose``
* ``sigType``

**BOB**

* ``tunnelNick``
* ``outhost``
* ``outport``

Important changes
=================

0.3.2
-----

* The default signature type for new Destinations is Ed25519.

  * If the SAM server does not support that (Java I2P 0.9.16 and earlier), txi2p
    will fall back on ECDSA_SHA256_P256, followed by the old default DSA_SHA1.

0.3
---

* Ports are now supported on the SAM API.

  * Previous ``port`` options are no longer ignored.
  * New ``localPort`` option for setting the client's local port.

* The ``SAMI2PStreamServerEndpoint`` API has changed to no longer require a
  reactor.

Documentation
=============

API documentation is available at https://txi2p.readthedocs.org

.. |txi2p| replace:: ``txi2p``
.. |clientFromString| replace:: ``clientFromString()``
.. |serverFromString| replace:: ``serverFromString()``

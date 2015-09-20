=====
txi2p
=====

|txi2p| is a set of I2P bindings for `Twisted <https://twistedmatrix.com/>`_
10.1 or greater.

|txi2p| supports both the SAM and BOB APIs for I2P. The default API is SAM.

Installation
============

You can install |txi2p| from PyPI::

    $ pip install txi2p

or by downloading the source and running::

    $ python setup.py install

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
    endpoint = SAMI2PStreamClientEndpoint.new(reactor, samEndpoint, 'stats.i2p')
    d = endpoint.connect(factory)

To have a server listen on an I2P Destination::

    from twisted.internet import reactor
    from twisted.internet.endpoints import clientFromString
    from txi2p.sam import SAMI2PStreamServerEndpoint

    samEndpoint = clientFromString(reactor, 'tcp:127.0.0.1:7656')
    endpoint = SAMI2PStreamServerEndpoint.new(reactor, samEndpoint, '/path/to/keyfile')
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

Clients
-------

Client string format::

    i2p:<host>[:port][:key=value]*

Supported arguments:

**SAM**

* ``nickname``
* ``autoClose``
* ``keyfile``
* ``options``

**BOB**

* ``tunnelNick``
* ``inhost``
* ``inport``
* ``options``

Servers
-------

Server string format::

    i2p:<keyfile>[:port][:key=value]*

Supported arguments:

**SAM**

* ``nickname``
* ``autoClose``
* ``options``

**BOB**

* ``tunnelNick``
* ``outhost``
* ``outport``
* ``options``

Documentation
=============

Will be available soon at https://txi2p.readthedocs.org

.. |txi2p| replace:: ``txi2p``
.. |clientFromString| replace:: ``clientFromString()``
.. |serverFromString| replace:: ``serverFromString()``

=====
txi2p
=====

``txi2p`` is a set of I2P bindings for `Twisted`_ 10.1 or greater.

Installation
==========

You can install ``txi2p`` from PyPI::

    $ pip install txi2p

or by downloading the source and running::

    $ python setup.py install

Endpoint strings
================

The Twisted plugin for ``clientFromString()`` and ``serverFromString()`` will
only work for `Twisted`_ 14.0 or greater.

Client string format: ``i2p:<host>[:port]``.
Server string format: ``i2p:<keyfile>[:port]``.

Both client and server strings support the following keyword arguments:

* ``api=<apiName>`` - Either ``SAM`` or ``BOB``.
* ``apiEndpoint=<endpointString>`` - An escaped client endpoint string pointing
  to the API, e.g. ``tcp\:127.0.0.1\:2827``.

APIs
====

I2P endpoints can be used with several APIs.

BOB
---

``BOBI2PClientEndpoint`` parameters:

* ``bobEndpoint`` - An endpoint that will connect to the BOB API.
* ``host`` - The I2P hostname or Destination to connect to.
* ``port`` (optional) - The port to connect to inside I2P. If unset or `None`,
  the default (null) port is used. Ignored because BOB doesn't support ports
  yet.
* ``tunnelNick`` (optional) - The tunnel nickname to use. If a tunnel with this
  nickname already exists, it will be used. The default is ``txi2p-#`` where
  ``#`` is the PID of the current process.

  * The implication of this is that by default, all endpoints (both client and
    server) created by the same process will use the same BOB tunnel.

* ``inhost`` (optional) - The host that the tunnel created by BOB will listen
  on. Defaults to ``localhost``.
* ``inport`` (optional) - The port that the tunnel created by BOB will listen
  on. Defaults to a port over 9000.

``BOBI2PServerEndpoint`` parameters:

* ``bobEndpoint`` - An endpoint that will connect to the BOB API.
* ``keypairPath`` - Path to a local file containing the keypair to use for the
  server Destination. If non-existent, new keys will be generated and stored.
* ``port`` (optional) - The port to listen on inside I2P. If unset or `None`,
  the default (null) port is used. Ignored because BOB doesn't support ports
  yet.
* ``tunnelNick`` (optional) - The tunnel nickname to use. If a tunnel with this
  nickname already exists, it will be used. The default is ``txi2p-#`` where
  ``#`` is the PID of the current process.

  * The implication of this is that by default, all endpoints (both client and
    server) created by the same process will use the same BOB tunnel.

* ``outhost`` (optional) - The host that the tunnel created by BOB will forward
  data to. Defaults to ``localhost``.
* ``outport`` (optional) - The port that the tunnel created by BOB will forward
  data to. Defaults to a port over 9000.

.. _Twisted: https://twistedmatrix.com/
.. _Twisted ticket #5069: https://twistedmatrix.com/trac/ticket/5069

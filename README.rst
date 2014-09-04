=====
txi2p
=====

``txi2p`` is a set of I2P bindings for `Twisted`_ 10.1 or greater.

Endpoint strings
================

The Twisted plugin for ``clientFromString()`` and ``serverFromString()`` will
only work for `Twisted`_ 14.0 or greater.

Client string format: ``i2p:<dest>[:port]``.
Server string format: ``i2p:<keypairPath>[:port]``.

Both client and server strings support the following keyword arguments:

* ``api=<apiName>`` - Currently only ``BOB``.
* ``apiEndpoint=<endpointString>`` - An escaped client endpoint string pointing
  to the API, e.g. ``tcp\:127.0.0.1\:2827``.

APIs
====

I2P endpoints will be backed by several APIs. BOB is the only one implemented.

BOB
---

``BOBI2PClientEndpoint`` parameters:

* ``bobEndpoint`` - An endpoint that will connect to the BOB API.
* ``dest`` - The I2P Destination to connect to.
* ``port`` (optional) - The port to connect to inside I2P. If unset or `None`,
  the default (null) port is used. Ignored because BOB doesn't support ports
  yet.
* ``tunnelNick`` (optional) - The tunnel nickname to use. If a tunnel with this
  nickname already exists, it will be used. The default is an auto-generated
  nickname.
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
  nickname already exists, it will be used. The default is an auto-generated
  nickname.
* ``outhost`` (optional) - The host that the tunnel created by BOB will forward
  data to. Defaults to ``localhost``.
* ``outport`` (optional) - The port that the tunnel created by BOB will forward
  data to. Defaults to a port over 9000.

.. _Twisted: https://twistedmatrix.com/
.. _Twisted ticket #5069: https://twistedmatrix.com/trac/ticket/5069

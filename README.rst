=====
txi2p
=====

``txi2p`` is a set of I2P bindings for `Twisted`_ 10.1 or greater.

APIs
====

I2P endpoints will be backed by several APIs. BOB is the only one implemented.

The Twisted plugin for ``clientFromString()`` and ``serverFromString()`` will
only work for `Twisted`_ ` 14.0 or greater

BOB
---

``BOBI2PClientEndpoint`` parameters:

* ``bobEndpoint`` - An endpoint that will connect to the BOB API.
* ``dest`` - The I2P Destination to connect to.
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
* ``tunnelNick`` (optional) - The tunnel nickname to use. If a tunnel with this
  nickname already exists, it will be used. The default is an auto-generated
  nickname.
* ``outhost`` (optional) - The host that the tunnel created by BOB will forward
  data to. Defaults to ``localhost``.
* ``outport`` (optional) - The port that the tunnel created by BOB will forward
  data to. Defaults to a port over 9000.

.. _Twisted: https://twistedmatrix.com/
.. _Twisted ticket #5069: https://twistedmatrix.com/trac/ticket/5069

=====
txi2p
=====

``txi2p`` is a set of I2P bindings for `Twisted <https://twistedmatrix.com/>`_
10.1 or greater.

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

Documentation
=============

Will be available soon at https://txi2p.readthedocs.org

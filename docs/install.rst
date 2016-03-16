============
Installation
============

Dependencies
============

``hsaudiotag3k`` requires Python 3.1. If you want to run the tests, you'll need `pytest <http://pytest.org/>`_.

Using setup.py
==============

It's a standard Distribute package, so if you've downloaded the source just use::

    python setup.py install

to install the package. If you haven't downloaded the source you should be download and install the package using pip::

    pip install hsaudiotag

for Python 2.x or::

    pip install hsaudiotag3k

for Python 3.x.

Building Documentation and other commands
=========================================

To build the sphinx documentation, just use::

    python setup.py build_sphinx

which will build the HTML documentation in the build/sphinx/html directory.

Other setup.py commands can be listed with::

    python setup.py --help-commands

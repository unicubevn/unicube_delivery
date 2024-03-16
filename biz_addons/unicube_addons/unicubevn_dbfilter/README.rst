====================
dbfilter_from_header
====================

This addon lets you pass a dbfilter as a HTTP header.

This is interesting for setups where database names can't be mapped to proxied host names.

**Table of contents**

.. contents::
   :local:

Installation
============

To install this module, you only need to add it to your addons, and load it as
a server-wide module.

This can be done with the ``server_wide_modules`` parameter in Odoo config file (ex: ``/etc/odoo.conf``)
or with the ``--load`` command-line parameter

``server_wide_modules = base,web,beanus_dbfilter``

Configuration
=============

Please keep in mind that the standard odoo dbfilter configuration is still
applied before looking at the regular expression in the header.

* For nginx, use:

  ``proxy_set_header X-dbfilter [your filter regex];``

* For caddy, use:

  ``proxy_header X-dbfilter [your filter regex]``

* For Apache, use:

  ``RequestHeader set X-dbfilter [your filter regex]``

And make sure that proxy mode is enabled in Odoo's configuration file:

``proxy_mode = True``

Usage
=====

To use this module, you need to complete installation and configuration
parts.

Bug Tracker
===========

Bugs are tracked on `GitHub Issues <https://github.com/OCA/server-tools/issues>`_.
In case of trouble, please check there if your issue has already been reported.
If you spotted it first, help us smashing it by providing a detailed and welcomed
`feedback <https://github.com/OCA/server-tools/issues/new?body=module:%20dbfilter_from_header%0Aversion:%2015.0%0A%0A**Steps%20to%20reproduce**%0A-%20...%0A%0A**Current%20behavior**%0A%0A**Expected%20behavior**>`_.

Do not contact contributors directly about support or help with technical issues.

Credits
=======

Authors
~~~~~~~

* The Beanuss

Maintainers
~~~~~~~~~~~

This module is maintained by the Beanus.

.. image:: https://odoo-community.org/logo.png
   :alt: Odoo Community Association
   :target: https://odoo-community.org


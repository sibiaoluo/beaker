# -*- coding: utf-8 -*-

"""
bkr whoami: Show your Beaker username
=====================================

.. program:: bkr whoami

Synopsis
--------

:program:`bkr whoami` [*options*]

Description
-----------

Prints to stdout a dict with username and proxied_by_username if proxy
permissions are granted to this user.

Options
-------

Common :program:`bkr` options are described in the :ref:`Options 
<common-options>` section of :manpage:`bkr(1)`.

Exit status
-----------

Non-zero on error, otherwise zero.

See also
--------

:manpage:`bkr(1)`
"""


from bkr.client import BeakerCommand


class WhoAmI(BeakerCommand):
    """Who Am I"""
    enabled = True


    def options(self):
        self.parser.usage = "%%prog %s" % self.normalized_name


    def run(self, *args, **kwargs):
        self.set_hub(**kwargs)
        print self.hub.auth.who_am_i()

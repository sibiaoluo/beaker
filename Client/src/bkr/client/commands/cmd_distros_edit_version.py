# -*- coding: utf-8 -*-

"""
bkr distros-edit-version: Edit the version of Beaker distros
============================================================

.. program:: bkr distros-edit-version

Synopsis
--------

:program:`bkr distros-edit-version` [*options*] --name=<name> <version>

Description
-----------

Applies the given version (for example, ``RedHatEnterpriseLinuxServer5.6`` or 
``Fedora14``) to all matching distros in Beaker.

Options
-------

.. option:: --name <name>

   All distros with the given name will be updated. <name> is interpreted as 
   a SQL LIKE pattern (the % character matches any substring).

Common :program:`bkr` options are described in the :ref:`Options 
<common-options>` section of :manpage:`bkr(1)`.

Exit status
-----------

Non-zero on error, otherwise zero.

Examples
--------

Set the version for all RHEL5.6 Server nightly trees from a particular date::

    bkr distros-edit-version --name "RHEL5.6-Server-20101110%" RedHatEnterpriseLinuxServer5.6

Notes
-----

This command is only available to Beaker administrators.

See also
--------

:manpage:`bkr(1)`
"""


from bkr.client import BeakerCommand


class Distros_Edit_Version(BeakerCommand):
    """Edit distros version"""
    enabled = True


    def options(self):
        self.parser.usage = "%%prog %s [options] <version>" % self.normalized_name

        self.parser.add_option(
            "--name",
            default=None,
            help="tag by name, use % for wildcard",
        )


    def run(self, *args, **kwargs):
        if len(args) < 1:
            self.parser.error("Please specify a version")

        name = kwargs.pop("name", None)
        version = str(args[0])

        self.set_hub(**kwargs)
        distros = self.hub.distros.edit_version(name, version)
        print "Updated the following distros with Version: %s" % version
        print "------------------------------------------------------"
        for distro in distros:
            print distro

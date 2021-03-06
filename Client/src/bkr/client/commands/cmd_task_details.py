# -*- coding: utf-8 -*-

"""
bkr task-details: Export details of a Beaker task
=================================================

.. program:: bkr task-details

Synopsis
--------

:program:`bkr task-details` [*options*] <task>...

Description
-----------

Prints to stdout details about each of the given tasks from Beaker's task 
library, one task per line.

This information is also available on the task page in the Beaker web UI.

Options
-------

.. option:: --invalid

   Print invalid task detail.

Common :program:`bkr` options are described in the :ref:`Options 
<common-options>` section of :manpage:`bkr(1)`.

Exit status
-----------

Non-zero on error, otherwise zero.

Examples
--------

Fetch details of the /distribution/beaker/dogfood task::

    bkr task-details /distribution/beaker/dogfood

See also
--------

:manpage:`bkr(1)`
"""


from bkr.client.task_watcher import *
from bkr.client import BeakerCommand
from optparse import OptionValueError
import sys
import os.path
import xmlrpclib
from xml.dom.minidom import Document, parseString


class Task_Details(BeakerCommand):
    """Show details about Task"""
    enabled = True

    def options(self):
        self.parser.usage = "%%prog %s [options] ..." % self.normalized_name
        self.parser.add_option(
            "--xml",
            default=False,
            action="store_true",
            help="print as xml",
        )
        self.parser.add_option(
            "--invalid",
            default=False,
            action="store_true",
            help="show invalid task",
        )

        self.parser.add_option(
            "--prettyxml",
            default=False,
            action="store_true",
            help="Pretty print the xml",
        )

    def run(self, *args, **kwargs):
        filter = dict()
        xml = kwargs.pop("xml")
        prettyxml = kwargs.pop("prettyxml")
        valid = True
        if kwargs.get("invalid"):
            valid = None

        self.set_hub(**kwargs)
        for task in args:
            if xml:
                print "%s\n%s" % (task, self.hub.tasks.to_xml(task, prettyxml, valid))
            elif prettyxml:
               print "%s\n%s" % (task, self.hub.tasks.to_xml(task, prettyxml, valid))
            else:
                print "%s %s" % (task, self.hub.tasks.to_dict(task,valid))

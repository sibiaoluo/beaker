
"""
bkr job-list: List Beaker jobs
==============================

.. program:: bkr job-list

Synopsis
--------

| :program:`bkr job-list` [*options*]
|       [--family=<family>] [--tag=<tag>] [--product=<cpeid>] [--completeDays=<days>]

Description
-----------

Prints to stdout a list of matching Beaker jobs.

.. _job-list-options:

Options
-------

.. option:: --family <family>

   Limit to jobs which ran with distro belonging to <family>, for example
   ``RedHatEnterpriseLinuxServer5``.

.. option:: --completeDays <days>

   Limit to jobs which finished at least <days> ago.

.. option:: --tag <tag>

   Limit to jobs which have retention tag <tag>, for example ``scratch``.

.. option:: --product <cpeid>

   Limit to jobs which were testing the product identified by <cpeid>.

.. option:: owner <username>

   Limit to jobs which are owned by the user identified by <username>.

.. option:: whiteboard <string>

   Limit to jobs whose whiteboard contains <string>

.. option:: mine

   Presence of --mine is equivalent to including own username in --owner

.. option:: --limit <number>

   Limit to displaying only the first <number> of results

.. option:: --min-id id

   Query jobs with a minium Job ID of id

.. option:: --max-id id

   Query jobs with a max Job ID of id

.. option:: --format list, --format json

   Display results in the given format. ``list`` lists one Job ID per
   line and is useful to be fed as input to other command line
   utilities. The default format is ``json``, which returns the Job
   IDs as a JSON string and is compact. This is useful for quick human observation.

Common :program:`bkr` options are described in the :ref:`Options
<common-options>` section of :manpage:`bkr(1)`.

Exit status
-----------

Non-zero on error, otherwise zero.

Examples
--------

List all scratch jobs which finished 30 or more days ago::

     bkr job-list --tag scratch --completeDays 30

List all scratch jobs with IDs between 10-100::

     bkr job-list --tag=scratch --min-id=10 --max-id=100

List all scratch jobs with min ID of 10::

     bkr job-list --tag=scratch --min-id=10


See also
--------

:manpage:`bkr(1)`
"""

from bkr.client import BeakerCommand
from optparse import OptionValueError

try:
    import json
except ImportError:
    import simplejson as json

class Job_List(BeakerCommand):
    """List Beaker jobs """
    enabled = True

    def options(self):
        self.parser.usage = "%%prog %s [options] ..." % self.normalized_name
        self.parser.add_option(
            "-f",
            "--family",
            help="Family for which the Job is run against"
        )

        self.parser.add_option(
            "-c",
            "--completeDays",
            type='int',
            help="Number of days job has been completed for"
        )

        self.parser.add_option(
            "-t",
            "--tag",
            action="append",
            help="Jobs with a particular tag"
        )

        self.parser.add_option(
            "-p",
            "--product",
            help="Jobs for a particular product"
        )

        self.parser.add_option(
            "-o",
            "--owner",
            help="Jobs with a particular owner"
        )

        self.parser.add_option(
            "-w",
            "--whiteboard",
            help="Jobs of a particular whiteboard"
        )

        self.parser.add_option(
            "--mine",
            default=False,
            action="store_true",
            help="Jobs owned by the querying user"
        )

        self.parser.add_option(
            "-l",
            "--limit",
            help="Place a limit on the number of results"
        )

        self.parser.add_option(
            "--min-id",
            type='int',
            help="Min Job ID to look into"
        )

        self.parser.add_option(
            "--max-id",
            type='int',
            help="Max Job ID to look into"
        )

        self.parser.add_option(
            '--format',
            type='choice',
            choices=['list', 'json'],
            default='json',
            help='Results display format: list, json [default: %default]',
        )

    def run(self,*args, **kwargs):
        family = kwargs.pop('family', None)
        tag = kwargs.pop('tag', None)
        product = kwargs.pop('product', None)
        complete_days = kwargs.pop('completeDays', None)
        owner = kwargs.pop('owner', None)
        whiteboard = kwargs.pop('whiteboard', None)
        mine = kwargs.pop('mine', None)
        limit = kwargs.pop('limit', None)
        format = kwargs['format']

        # Process Job IDs if specified and sanity checking
        minid = kwargs.pop('min_id', None)
        maxid = kwargs.pop('max_id', None)
        if minid or maxid:
            if minid and minid<=0 or maxid and maxid <= 0:
                self.parser.error('Please specify a non zero positive Job ID')
            if minid and maxid:
                if maxid <  minid:
                    self.parser.error('Max Job ID should be greater than or equal to min Job ID')

        if complete_days is not None and complete_days < 1:
            self.parser.error('Please pass a positive integer to completeDays')

        if complete_days is None and tag is None and family is None and product is None\
                and owner is None and mine is None and whiteboard is None:
            self.parser.error('Please pass either the completeDays time delta, a tag, product, family, or owner')

        self.set_hub(**kwargs)
        jobs = self.hub.jobs.filter(dict(tag=tag,
                                        daysComplete=complete_days,
                                        family=family,
                                        product=product,
                                        owner=owner,
                                        whiteboard=whiteboard,
                                        mine=mine,
                                        minid=minid,
                                        maxid=maxid,
                                        limit=limit))
        
        if format == 'list':
            for job_id in jobs:
                print job_id
                
        if format == 'json':
            print json.dumps(jobs)

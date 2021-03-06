What's New
==========

This document covers major changes to Beaker in each release. It is aimed
at users and administrators of existing Beaker installations that are
being upgraded to a new version.


.. For developers

   During the development cycle, just add new release notes as separate
   files in the appropriate release directory without worrying about
   the relative order. Once the release is declared feature complete
   and ready for formal testing, then wildcard entry will be replaced
   with an explicit list that puts the subsections in some kind of
   sensible order.


.. release notes for 1.0 follow... uncomment these when 1.0 is a real thing again

    What's new in Beaker 1.0?
    -------------------------

    After more than 5 years of active development, Beaker is finally taking the
    plunge and declaring a 1.0 release!

    The primary new feature in Beaker 1.0 is the initial implementation of the
    :ref:`proposal-enhanced-user-groups` design proposal.

    .. toctree::
       :maxdepth: 2
       :glob:

       release-1.0/*

Unreleased changes
------------------

The following changes will appear in the next Beaker release.

.. toctree::
   :maxdepth: 2
   :glob:

   next/*

Beaker 0.13
-----------

Beaker 0.13 includes a number of new features and bug fixes, focusing on
the `Enhanced User Groups <../../dev/proposals/enhanced-user-groups.html>`__ 
design proposal.

.. toctree::
   :maxdepth: 2

   release-0.13
   upgrade-0.13

Beaker 0.12
-----------

Beaker 0.12 includes a number of new features and bug fixes.

.. toctree::
   :maxdepth: 2

   release-0.12
   upgrade-0.12

Beaker 0.11
-----------

Beaker 0.11 brings improvements to reporting and metrics collection, as well as 
a number of minor enhancements and bug fixes.

.. toctree::
   :maxdepth: 2

   release-0.11
   upgrade-0.11

Older releases
--------------

Release notes for versions prior to 0.11 are not available.

For administrators upgrading from older versions, refer to the now-obsolete 
`SchemaUpgrades directory 
<http://git.beaker-project.org/cgit/beaker/tree/SchemaUpgrades/>`_ in Beaker's 
source tree. (Those files were previously included in the beaker-server package 
under ``/usr/share/doc/beaker-server-*``.)

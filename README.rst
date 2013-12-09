Introduction
============

SugarCRM_ is an open-source software-solution vendor which produces the Sugar
Customer Relationship Management (CRM) system.

This add-on provide components to use SugarCRM in Plone.

How to install
==============

.. image:: https://pypip.in/v/collective.sugarcrm/badge.png
    :target: https://crate.io/packages/collective.sugarcrm/

.. image:: https://pypip.in/d/collective.sugarcrm/badge.png
    :target: https://crate.io/packages/collective.sugarcrm/

.. image:: https://secure.travis-ci.org/collective/collective.sugarcrm.png
    :target: http://travis-ci.org/#!/collective/collective.sugarcrm

.. image:: https://coveralls.io/repos/collective/collective.sugarcrm/badge.png?branch=master
    :target: https://coveralls.io/r/collective/collective.sugarcrm


This addon can be installed has any other addons. please follow official
documentation_

.. _documentation: http://plone.org/documentation/kb/installing-add-ons-quick-how-to


tests
-----

Integration tests are run with a trial URL
If it is not available, please fill the demand for a new demo at
http://www.sugarcrm.com/webform/try-sugarcrm-free-7-days and 
update the sugarcrm part of the buildout.

you can exclude integration tests with sugarcrm by using
use ./bin/test -t UnitTest

Components
==========

pasplugin
---------

A PAS plugin has been implemented. You can logged into Plone with sugarcrm
credentials.

webservice
----------

suds_ has been used to provide a simple api over soap's sugarcrm.

  >>> webservice = ISugarCRM(context)
  >>> results = webservice.search(query_string='JeanMichel')

source
------

z3c.formwidget.query.interfaces.IQuerySource for contacts and accounts are
provided.

password
--------

A utility is available to crypt password for using with webservice (sic)

portlet contact
---------------

With a condition on collective.portlet.contact installed,
it provides a backend from your sugarCRM contact address book to the
contact portlet

Credits
=======

Companies
---------

|makinacom|_


People
------

- JeanMichel FRANCOIS aka toutpt <toutpt@gmail.com>

.. |makinacom| image:: http://depot.makina-corpus.org/public/logo.gif
    :alt: Makina Corpus
.. _makinacom:  http://www.makina-corpus.com
.. _suds: https://fedorahosted.org/suds
.. _sugarcrm: http://www.sugarcrm.com/crm

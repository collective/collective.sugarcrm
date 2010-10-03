Introduction
============

SugarCRM is an open-source software-solution vendor which produces the Sugar
Customer Relationship Management (CRM) system.

This add-on provide components to use SugarCRM in Plone.

Status
======

Under heavy developpement for SugarCRM 6.0

Found a bug with get_entry, doesn't return any results with a good id.

No tests at all.

Components
==========

pasplugin
---------

IAuthenticationPlugin has been implemented to provide a way to login with
sugarcrm credentials

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

INSTALL
=======

A generic setup is registred to setup the pas plugin and needed properties
to configure access to the sugarcrm instance you want to use

Credits
=======

Companies
---------

|makinacom|_

  * `Planet Makina Corpus <http://www.makina-corpus.org>`_
  * `Contact us <mailto:python@makina-corpus.org>`_


Authors

  - JeanMichel FRANCOIS aka toutpt <toutpt@gmail.com>

Contributors

.. |makinacom| image:: http://depot.makina-corpus.org/public/logo.gif
.. _makinacom:  http://www.makina-corpus.com

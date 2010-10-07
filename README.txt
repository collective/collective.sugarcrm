Introduction
============

SugarCRM is an open-source software-solution vendor which produces the Sugar
Customer Relationship Management (CRM) system.

This add-on provide components to use SugarCRM in Plone.

Status
======

Useable in production

tests
-----

Tests are run with this URL: http://trial.sugarcrm.com/wbnawe7415/service/v2/soap.php
If it is not available, please fill the demand for a new demo at
http://www.sugarcrm.com/crm/ondemand_eval.html and export the URL into
environnement:

  export SUGARCRM_SOAP_URL="NEW TRIAL URL"

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

portlet contact
---------------

With a condition on collective.portlet.contact installed,
it provides a backend from your sugarCRM contact address book to the
contact portlet

INSTALL
=======

A generic setup is registred to setup the pas plugin and needed properties
to configure access to the sugarcrm instance you want to use. A control panel
is added to let you configure access to sugarcrm.

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

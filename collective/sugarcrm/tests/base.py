import unittest

#from zope.testing import doctestunit
#from zope.component import testing
from Testing import ZopeTestCase as ztc

from Products.Five import fiveconfigure
from Products.PloneTestCase import PloneTestCase as ptc
from Products.PloneTestCase.layer import PloneSite
ptc.setupPloneSite(products=['collective.sugarcrm'])

import collective.sugarcrm
from collective.sugarcrm.tests import utils

class TestCase(ptc.PloneTestCase):

    class layer(PloneSite):

        @classmethod
        def setUp(cls):
            fiveconfigure.debug_mode = True
            ztc.installPackage(collective.sugarcrm)
            fiveconfigure.debug_mode = False

        @classmethod
        def tearDown(cls):
            pass


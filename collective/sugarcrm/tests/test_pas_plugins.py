import unittest
from collective.sugarcrm import pasplugin
from collective.sugarcrm.tests import utils
from collective.sugarcrm import password

class FakeSugarCRM(object):
    def search(self):
        return []

    def login(self, username, password, crypt=False):
        if username == 'will':
            return 'sessionID'

class Test(unittest.TestCase):

    def setUp(self):
        #remove components:
        def _sugarcrm(instance):
            return FakeSugarCRM()
        def _password(instance):
            return password.Password()
        pasplugin.AuthPlugin._sugarcrm = _sugarcrm
        pasplugin.AuthPlugin._passord_utility = _password
        self.plugin = pasplugin.AuthPlugin(id='myplugin')

    def test_authenticateCredentials(self):
        res = self.plugin.authenticateCredentials({})
        self.failUnless(res is None)
        credentials = {'login':'will', 'password':'will'}
        res = self.plugin.authenticateCredentials(credentials)
        self.failUnless(res == ('will','will'))
        credentials = {'login':'badid', 'password':'will'}
        res = self.plugin.authenticateCredentials(credentials)
        self.failUnless(res is None)

    def test_enumerateUsers(self):
        pass

    def test_getPropertiesForUser(self):
        pass

def test_suite():
    return unittest.makeSuite(Test)


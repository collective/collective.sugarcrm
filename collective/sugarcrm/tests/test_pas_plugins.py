import unittest
from collective.sugarcrm import pasplugin
from collective.sugarcrm import password
from collective.sugarcrm.tests import base, utils

class FakeSugarCRM(object):
    def search(self, session=None, query_string='', module='Contacts',
                offset="0", max="100"):
        if module!='Users':
            return []
        if not query_string:
            return []
        results = []
        if query_string == 'will':
            results.append({'user_name':'will','email_address':'will@sugarcrm.com',
                            'first_name':u'Will', 'last_name':u'DUPONT'})
        return results

    def login(self, username, password, crypt=False):
        if username == 'will':
            return 'sessionID'

class FakePropertiedUser(object):
    def __init__(self):
        self.id = 'will'
        self.login = 'will'
    
    def getUserName(self):
        return self.id

class UnitTest(unittest.TestCase):

    def setUp(self):
        #remove components:
        def _sugarcrm(instance):
            return FakeSugarCRM()
        def _password(instance):
            return password.Password()
        self._sugarcrm = pasplugin.SugarCRMPASPlugin._sugarcrm
        self._password = pasplugin.SugarCRMPASPlugin._passord_utility
        pasplugin.SugarCRMPASPlugin._sugarcrm = _sugarcrm
        pasplugin.SugarCRMPASPlugin._passord_utility = _password
        self.plugin = pasplugin.SugarCRMPASPlugin(id='myplugin')
        self.plugin._activated = True
    
    def tearDown(self):
        pasplugin.SugarCRMPASPlugin._sugarcrm = self._sugarcrm
        pasplugin.SugarCRMPASPlugin._passord_utility = self._password

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
        keys = ('id','login','pluginid','editurl')
        id = 'will'
        res = self.plugin.enumerateUsers(id=id, exact_match=True)
        self.failUnless(len(res)==1)
        self.failUnless(res[0]['id']=='will')
        id = ['will']
        res = self.plugin.enumerateUsers(id=id, exact_match=True)
        self.failUnless(len(res)==1)
        self.failUnless(res[0]['id']=='will')
        for k in keys:
            self.failUnless(k in res[0].keys())

        login = 'will'
        res = self.plugin.enumerateUsers(login=login, exact_match=True)
        self.failUnless(len(res)==1)
        self.failUnless(res[0]['login']=='will')
        for k in keys:
            self.failUnless(k in res[0].keys())

    def test_getPropertiesForUser(self):
        user = FakePropertiedUser()
        properties = self.plugin.getPropertiesForUser(user)
        self.failUnless(type(properties) == dict)
        keys = ('email', 'fullname')
        for k in keys:
            self.failUnless(k in properties.keys(), properties.keys())

class IntegrationTest(base.TestCase):
    def afterSetUp(self):
        self.plugin = self.portal.acl_users.sugarcrm
        self.sugarcrm_config = self.portal.portal_properties.sugarcrm
        self.sugarcrm_config._updateProperty('soap_url', utils.SOAP['soap_url'])
        self.sugarcrm_config._updateProperty('soap_username',
                                             utils.SOAP['soap_username'])
        self.sugarcrm_config._updateProperty('soap_password',
                                             utils.SOAP['soap_password'])
        self.sugarcrm_config._updateProperty('activate_service',True)
        self.sugarcrm_config._updateProperty('activate_pasplugin',True)
        self.plugin._activated = True

    def test_authenticateCredentials(self):
        credentials = {'login':'will', 'password':'will'}
        res = self.plugin.authenticateCredentials(credentials)
        self.failUnless(res==('will','will'))

    def test_enumerateUsers(self):
        keys = ('id','login','pluginid','editurl')
        id = 'will'
        res = self.plugin.enumerateUsers(id=id)
        self.failUnless(len(res)==1)
        user_info = res[0]
        for k in keys:
            self.failUnless(k in user_info.keys())

        id = ['will']
        res = self.plugin.enumerateUsers(id=id)
        self.failUnless(len(res)==1)
        
        login = 'will'
        res = self.plugin.enumerateUsers(login=login)
        self.failUnless(len(res)==1)

        login = ['will']
        res = self.plugin.enumerateUsers(login=login)
        self.failUnless(len(res)==1)

    def test_getPropertiesForUser(self):
        user = FakePropertiedUser()
        properties = self.plugin.getPropertiesForUser(user)
        self.failUnless('email' in properties.keys())
        self.failUnless('fullname' in properties.keys())

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(UnitTest))
    suite.addTest(unittest.makeSuite(IntegrationTest))
    return suite

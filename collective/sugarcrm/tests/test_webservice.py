import unittest
from collective.sugarcrm.webservice import WebService
from collective.sugarcrm import interfaces
from collective.sugarcrm.tests import utils
from zope.interface import verify

from zope.component import getGlobalSiteManager
from collective.sugarcrm.password import Password
import suds

class FakeFactory(object):
    def create(self, argument_type):
        if argument_type == 'user_auth':
            return FakeUserAuth()

class FakeUserAuth(object):
    def __init__(self):
        self.user_name = None
        self.password = None

class FakeService(object):
    def login(self, user):
        if user.user_name == 'will':
            return 'session'
        raise suds.WebFault("Invalid Login")

class FakeClient(object):
    def __init__(self):
        self.factory = FakeFactory()
        self.service = FakeService()


class UnitTest(unittest.TestCase):

    def setUp(self):
        self.ws = WebService(None)
        self.ws._client = FakeClient()
    
    def test_client(self):
        self.failUnless(type(self.ws.client)==FakeClient)

    def test_create(self):
        created = self.ws.create('user_auth')
        self.failUnless(type(created)==FakeUserAuth)

    def test_login(self):
        login = self.ws.login('will', 'will')
        self.failUnless(login == 'session')
        #TODO: check raise

    def test_session(self):
        pass
    
    def test_search(self):
        pass
    
    def test_get_entry(self):
        pass
    
    def test_get_module_fields(self):
        pass

class IntegrationTest(unittest.TestCase):
    """Integration test with the real webservice. Check utils
    and update with a good free trial demo of SugarCRM"""

    def setUp(self):
        self.url = utils.SOAP['soap_url']
        self.username = utils.SOAP['soap_username']
        self.password = utils.SOAP['soap_password']
        self.ws = WebService(None,
                             url=self.url,
                        username=self.username,
                        password=self.password)
        gsm = getGlobalSiteManager()
        passwordUtility = Password()
        gsm.registerUtility(passwordUtility, interfaces.IPasswordEncryption)

    def test_init(self):
        ws = self.ws
        self.assertEqual(ws.context, None)
        self.assertEqual(ws.url, self.url)
        self.assertEqual(ws.username, self.username)
        self.assertEqual(ws.password, self.password)
        self.assert_(ws.client is not None)
        #check interface implementation
        self.assert_(interfaces.ISugarCRM.providedBy(ws))
        try:
            self.failUnless(verify.verifyObject(interfaces.ISugarCRM, ws))
        except verify.BrokenImplementation, e:
            self.fail(str(e))

    def test_create(self):
        user_auth = self.ws.create('user_auth')
        self.assert_(user_auth is not None)
        self.assert_(hasattr(user_auth, 'user_name'))
        self.assert_(hasattr( user_auth, 'password'))

    def test_entry2dict(self):
        #TODO
        pass

    def test_login(self):
        login = self.ws.login(self.username, self.password, crypt=True)
        self.assertNotEqual(login.id, "-1")
        self.assert_(login.module_name == "Users")
        info = self.ws._entry2dict(login)
        self.assert_(info['user_name'],self.username)
        self.assert_('user_currency_id' in info)
        self.assert_('user_id' in info)
        self.assert_('user_currency_name' in info)
        self.assert_('user_language' in info)

    def test_logout(self):
        login = self.ws.login(self.username, self.password, crypt=True)
        self.ws.logout(login.id)
        self.failUnlessRaises(suds.WebFault,
                          self.ws.search,
                          login.id, utils.CONTACT['first_name'])

    def test_session(self):
        session = self.ws.session
        session2 = self.ws.session
        self.assert_(type(session)==str)
        self.assertEqual(session, session2)

    def test_search(self):
        results = self.ws.search(query_string=utils.CONTACT['first_name'])
        jerald = results[0]
        self.assertEqual(jerald['name'], utils.CONTACT['name'])
        for k in ('name', 'phone_work', 'title', 'assigned_user_name',
                  'account_name', 'id'):
            self.assert_(k in jerald.keys(), '%s not in results'%k)

    def test_get_entry(self):
        results = self.ws.search(query_string='jerald')
        id = results[0]['id']
        entry = self.ws.get_entry(id=id)
        self.assertEqual(entry['first_name'],utils.CONTACT['first_name'])
        self.assertEqual(entry['last_name'], utils.CONTACT['last_name'])
        self.assertEqual(entry['primary_address_city'],utils.CONTACT['city'])

    def test_get_module_fields(self):
        #TODO
        pass

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(UnitTest))
    suite.addTest(unittest.makeSuite(IntegrationTest))
    return suite

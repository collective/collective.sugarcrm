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

class FakeLoggedIn(object):
    def __init__(self, id):
        self.id = id

class FakeFault(object):
    def __init__(self):
        self.faultstring = "Invalid Login"

class FakeResults(object):
    def __init__(self, entry_list=[]):
        self.entry_list= entry_list

class FakeService(object):
    def __init__(self):
        #marker specific for tests
        self.logged = False

    def login(self, user):
        if user.user_name == 'will':
            self.logged = True
            return FakeLoggedIn('session')
        raise suds.WebFault(FakeFault(), None)

    def logout(self, session):
        if session == 'session':
            self.logged = False
        
    def search_by_module(self, session, query_string, modules, offset, max):
        if session=='session' and query_string and len(modules)>0:
            pass #tired to create new fake classes
        return []

class FakeClient(object):
    def __init__(self):
        self.factory = FakeFactory()
        self.service = FakeService()


class UnitTest(unittest.TestCase):

    def setUp(self):
        self.ws = WebService(None)
        self.ws._client = FakeClient()
        self.ws.activated = True
        def password():
            return Password()
        self.ws.password_utility = password
        self.ws.username = 'will'

    def test_activated(self):
        ws = WebService(None)
        self.failUnless(ws.activated==False)
        self.failUnless(self.ws.activated==True)

    def test_client(self):
        self.failUnless(type(self.ws.client)==FakeClient)

    def test_create(self):
        created = self.ws.create('user_auth')
        self.failUnless(type(created)==FakeUserAuth, created)

    def test_login(self):
        login = self.ws.login('will', 'will')
        self.failUnless(login.id == 'session')
        self.failUnless(self.ws.login('', '') is None)

    def test_logout(self):
        self.ws.logout('session')
        self.failUnless(self.ws._client.service.logged == False)

    def test_session(self):
        session = self.ws.session
        self.failUnless(session=='session')
        self.ws.username = ''
        session = self.ws.session
        self.failUnless(session is None)

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
                        password=self.password,
                        activated=True)
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
        self.assert_(ws.activated==True)
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

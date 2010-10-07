import unittest
from collective.sugarcrm.webservice import WebService
from collective.sugarcrm import interfaces
from collective.sugarcrm.tests import utils
from zope.interface import verify

from zope.component import getGlobalSiteManager
from collective.sugarcrm.password import Password
import suds

class TestWebService(unittest.TestCase):
    def setUp(self):
        self.url = utils.DEMO['soap_url']
        self.username = utils.DEMO['soap_username']
        self.password = utils.DEMO['soap_password']
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
                          login.id, 'jerald')

    def test_session(self):
        session = self.ws.session
        session2 = self.ws.session
        self.assert_(type(session)==str)
        self.assertEqual(session, session2)

    def test_search(self):
        results = self.ws.search(query_string='jerald')
        jerald = results[0]
        self.assertEqual(len(results),1)
        self.assertEqual(jerald['name'],'Jerald Arenas')
        for k in ('name', 'phone_work', 'title', 'assigned_user_name',
                  'account_name', 'id'):
            self.assert_(k in jerald.keys(), '%s not in results'%k)

    def test_get_entry(self):
        results = self.ws.search(query_string='jerald')
        id = results[0]['id']
        entry = self.ws.get_entry(id=id)
        self.assertEqual(entry['first_name'],'Jerald')
        self.assertEqual(entry['last_name'],'Arenas')
        self.assertEqual(entry['primary_address_city'],'Cupertino')

    def test_get_module_fields(self):
        #TODO
        pass

def test_suite():
    return unittest.makeSuite(TestWebService)


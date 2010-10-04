from suds.client import Client
from collective.sugarcrm import interfaces
from zope import component
from zope import interface
from Products.CMFCore.utils import getToolByName
import logging

logger = logging.getLogger('collective.sugarcrm')

class WebService(object):
    """Code base between normal and loggedin component"""
    
    interface.implements(interfaces.IComplexArgFactory,
                         interfaces.ISugarCRM)

    def __init__(self, context, url="", username="", password=""):
        """If context is not, you must provide url"""

        if context is not None:
            #get url
            pptool = getToolByName(context, 'portal_properties')
            url = pptool.sugarcrm.soap_url.encode('utf-8')
            username = pptool.sugarcrm.soap_username.encode('utf-8')
            password = pptool.sugarcrm.soap_password.encode('utf-8')

        self.context = context
        self.url = url
        self.username = username
        self.password = password
        self.client = Client(self.url+'?wsdl')
        self._session = None

    def create(self, argument_type):
        """Create arguements types.
        
        How to use it:
        >>> crm = SugarCRM(None, "http://trial.sugarcrm.com/mwlcpt5183")
        >>> auth = crm.create("user_auth")
        >>> auth.user_name = "admin"
        >>> auth.password = "blabla"

        There are 120 available types on SugarCRM 6. To get types, just print
        print the suds client on current output
        """
        return self.client.create(argument_type)

    def _get_info(self, entry, name_value_list=True):
        info = {}
        if name_value_list:
            entry = entry.name_value_list
        for item in entry:
            info[item.name] = item.value
        return info

    def login(self, username, password):
        user = self.client.factory.create('user_auth')
        user.user_name = username
        user.password = password
        login = self.client.service.login(user)
        return login

    def logout(self, session):
        self.client.service.logout(session)


    @property
    def session(self):

        if self._session: return self._session
        utility = component.getUtility(interfaces.IPasswordEncryption)
        user = self.client.factory.create('user_auth')

        user.user_name = self.username
        user.password = utility.crypt(self.password)
        login = self.client.service.login(user)

        if login.id != "-1":
            self._session = login.id

        return self._session

    def search(self, session=None, query_string='', module='Contacts', offset=0,
                      max=100):
        """search a contact or whatevery you want. The search is based on
        query_string argument and given module (default to Contacts)
        
        Return a list of dict with all the content from the response
        """
        
        if session is None:
            session = self.session

        results = self.client.service.search_by_module(session,
                                                       query_string,
                                                       [module],
                                                       offset, max)
        entry_list = results.entry_list

        infos = []
        for m in entry_list:
            for entry in m.records:
                infos.append(self._get_info(entry, name_value_list=False))

        return infos

    def get_entry(self, session=None, module='Contacts',  uid='',
                  select_fields=[]):
        """get one entry identified by the uid argument. Type of entry
        is defined by the given module. Default to "Contacts"""

        if session is None:
            session = self.session
        
        if not select_fields:
    
            fields = self.get_module_fields(session, module)
            select_fields = [field.name for field in fields]

        results = self.client.service.get_entry(session, module, uid,
                                                select_fields)
        (entry,) = results.entry_list

        info = self._get_info(entry)

        return info

    def get_module_fields(self, session=None, module="Contacts"):

        if session is None:
            session = self.session

        results = self.client.service.get_module_fields(session, module)
        module_fields = results.module_fields

        fields = [field for field in module_fields]

        return fields

if __name__ == "__main__":
    url="http://mydoamin.com/soap.php"
    username = "admin"
    password = "admin"
    contact_firstname = "Arnaud"
    account_name = "Makina"

    #register password utility
    from zope.component import getGlobalSiteManager
    from collective.sugarcrm.password import Password
    gsm = getGlobalSiteManager()
    passwordUtility = Password()
    gsm.registerUtility(passwordUtility, interfaces.IPasswordEncryption)

    service = WebService(None, url=url, username=username,
                               password=password)

    sid = service.session
    contacts = service.search(query_string=contact_firstname)
    contact = service.get_entry(uid=contacts[0]['id'])
    if not contact:
        print "ERROR can't find %s with get_entry"%contacts[0]
    accounts = service.search(query_string=account_name, module="Accounts")
    account = service.get_entry(uid=accounts[0]['id'], module="Accounts")
    if not account:
        print "ERROR can't find %s with get_entry"%accounts[0]

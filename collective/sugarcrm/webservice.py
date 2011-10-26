from suds.client import Client
from collective.sugarcrm import interfaces
from zope import component
from zope import interface
from Products.CMFCore.utils import getToolByName
import logging
from z3c_suds import get_suds_client
from suds.client import Client
from plone.memoize import ram
from time import time
from suds import WebFault

logger = logging.getLogger('collective.sugarcrm')

METHODS = ('login', 'logout', 'get_entry', 'search_by_module', 'get_module_fields')

def session_cache_key(fun, self):
    #5 minutes
    username = self.username
    password = self.password
    five_minute = str(time() // (5*60))
    return five_minute + username + password

def get_entry_cache_key(fun, self, session=None, module='Contacts',  id='',
                  select_fields=[]):
    #one hour + module + id
    one_hour = str(time() // (60*60))
    cache_key = one_hour +"-"+ module +"-"+ id
    return cache_key

def get_module_fields_cache_key(fun, self, session=None, module="Contacts"):
    one_hour = str(time() // (60*60))
    cache_key = one_hour +"-"+ module
    return cache_key


class WebService(object):
    """Code base between normal and loggedin component"""
    
    interface.implements(interfaces.IComplexArgFactory,
                         interfaces.ISugarCRM)

    def __init__(self, context, url="", username="", password="", activated=False):
        """If context is not, you must provide url"""

        if context is not None:
            #get url
            pptool = getToolByName(context, 'portal_properties')
            url = pptool.sugarcrm.soap_url.encode('utf-8')
            username = pptool.sugarcrm.soap_username.encode('utf-8')
            password = pptool.sugarcrm.soap_password.encode('utf-8')
            activated = pptool.sugarcrm.activate_service

        self.context = context
        self.activated = activated
        self.url = url
        self._valid_url = False
        self.username = username
        self.password = password
        self._valid_credentials = None
        self._client = None

        #self.client = Client(self.url+'?wsdl')
        self._module_fields = {}

    @property
    def client(self):
        if not self.activated: return
        if self._client is not None:
            return self._client
        client = None
        try:
            url = self.url+'?wsdl'
            #fix 404 exception on login: http://stackoverflow.com/questions/6499770/why-am-i-getting-exception-404-unot-found-with-suds
            client = get_suds_client(url, context=self.context, location=url)
        except ValueError, e:
            logger.error("invalid SOAP URL: client instanciation fail")
        valid = True #try now to validate the existing client
        if client is not None:
            for method in METHODS:
                if not hasattr(client.service, method):
                    logger.error("invalid SOAP URL: no %s"%method)
                    valid = False
                    break
        if not valid:
            client = None
        if client is not None:
            self._client = client
        else:
            logger.error("client is none:%s %s %s"%(self.url,self.username,
                                                    self.password))
        return client

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
        if not self.activated: return
        if self.client is not None:
            return self.client.factory.create(argument_type)

    def _entry2dict(self, entry, name_value_list=True):
        info = {}
        if name_value_list:
            entry = entry.name_value_list
        for item in entry:
            info[item.name] = item.value
        return info

    def login(self, username, password, crypt=False):
        if not self.activated: return
        if self.client is None: return

        user = self.client.factory.create('user_auth')
        user.user_name = username
        if not crypt:
            user.password = password
        else:
            utility = self.password_utility()
            user.password = utility.crypt(password)
        try:
            login = self.client.service.login(user)
        except WebFault, e:
            if e.fault.faultstring == "Invalid Login":
                logger.error('invalid login: %s %s %s'%(username,
                                                        password, crypt))
                return None
            raise e
        return login

    def password_utility(self):
        return component.getUtility(interfaces.IPasswordEncryption)

    def logout(self, session):
        if not self.activated: return
        if self.client is None: return
        self.client.service.logout(session)

    @property
    def session(self):
        """Return the session of loggedin portal soap account"""

        if not self.activated: return
        if self.client is None: return

        login = self.login(self.username, self.password, crypt=True)
        if login is not None:
            logger.debug('ws.session -> %s'%login.id)
            return str(login.id)

        logger.debug('ws.session -> None')

    def search(self, session=None, query_string='', module='Contacts',
                offset="0", max="100"):
        """search a contact or whatevery you want. The search is based on
        query_string argument and given module (default to Contacts)
        
        Return a list of dict with all the content from the response
        """

        if not self.activated: return[]
        if self.client is None: return []
        if session is None: #session as arg
            session = self.session
        if session is None: #session is invalid
            return []
        if type(query_string) == unicode:
            query_string = query_string.encode('utf-8')

        results = self.client.service.search_by_module(session,
                                                       query_string,
                                                       [module],
                                                       offset, max)
        entry_list = results.entry_list

        infos = []
        for m in entry_list:
            for entry in m.records:
                infos.append(self._entry2dict(entry, name_value_list=False))

        logger.debug('ws.search %s -> %s results'%(query_string, len(infos)))
        return infos


    def get_entry(self, session=None, module='Contacts',  id='',
                  select_fields=[]):

        if not self.activated: return
        if self.client is None: return
        if session is None: #session as arg
            session = self.session
        if session is None: #session is invalid
            return {}

        if not select_fields:
            #you can't call a cached method from an other cached method
            if module in self._module_fields:
                fields = self._module_fields[module]
            else:
                fields = self.get_module_fields(session=str(session),
                                                 module=str(module))
            select_fields = [field for field in fields]

        results = self.client.service.get_entry(session, module, id,
                                                select_fields)
        (entry,) = results.entry_list

        info = self._entry2dict(entry)

        #logger.debug(u'ws.get_entry(%s, %s) -> %s'%(module, id, info))
        return info

    def get_module_fields(self, session=None, module="Contacts"):

        if not self.activated: return []
        if self.client is None: return []
        if session is None: #session as arg
            session = self.session
        if session is None: #session is invalid
            return []

        results = self.client.service.get_module_fields(session, module)
        module_fields = results.module_fields

        fields = [str(field.name) for field in module_fields]
        self._module_fields[module] = fields

        return fields

class WebServiceCached(WebService):

    @property
    @ram.cache(session_cache_key)
    def session(self):
        return super(WebServiceCached, self).session

    @ram.cache(get_entry_cache_key)
    def get_entry(self, session=None, module='Contacts',  id='',
                  select_fields=[]):
        return super(WebServiceCached, self).get_entry(session=session,
                                                 module=module,
                                                 id=id,
                                                 select_fields=select_fields)

    @ram.cache(get_module_fields_cache_key)
    def get_module_fields(self, session=None, module="Contacts"):
        return super(WebServiceCached, self).get_module_fields(session=session,
                                                         module=module)


import logging
logger = logging.getLogger('collective.sugarcrm')
import copy

from Products.PluggableAuthService import plugins
from Products.PluggableAuthService import interfaces
from Products.PluggableAuthService import utils

from App.class_init import InitializeClass
from OFS.Cache import Cacheable

from zope import component
from zope import interface

from collective.sugarcrm.interfaces import IPasswordEncryption, ISugarCRM
from AccessControl import ClassSecurityInfo
from Products.CMFCore.utils import getToolByName

class ISugarCRMPASPlugin(interface.Interface):
    """Marker interface"""

class SugarCRMPASPlugin(plugins.BasePlugin.BasePlugin):
    """This plugin try to authenticate the user
    with the login method of the sugarcrm webservice"""
    
    interface.implements(interfaces.plugins.IAuthenticationPlugin,
                         interfaces.plugins.IUserEnumerationPlugin,
                         interfaces.plugins.IPropertiesPlugin,
                         ISugarCRMPASPlugin)

    meta_type = 'SugarCRM IAuthenticationPlugin'
    security = ClassSecurityInfo()
    
    def __init__(self, id, title=None):
        self.id = id
        self.title = title
        self._activated = None
        self._v_blacklist_ids = []

    def _passord_utility(self):
        return component.getUtility(IPasswordEncryption)

    def _sugarcrm(self):
        return ISugarCRM(self)

    @property
    def activated(self):
        """Return True if webservice and pasplugin are activated"""
        if self._activated is not None:
            return self._activated
        pp = getToolByName(self, 'portal_properties').sugarcrm
        return bool(pp.activate_pasplugin)

    security.declarePrivate('authenticateCredentials')
    def authenticateCredentials(self, credentials):
        """ See IAuthenticationPlugin.
        """
        if not self.activated:return
        login = credentials.get('login')
        password = credentials.get('password')

        if not login or not password:
            return

        if self.isInBlacklist('%s-%s'%(login, password)):
            return

        logger.info('authenticateCredentials not cached %s'%login)

        utility = self._passord_utility()
        encrypted_password = utility.crypt(password)

        sugarcrm = self._sugarcrm()
        session = sugarcrm.login(login, encrypted_password)

        if session is None:
            self.addToBlacklist('%s-%s'%(login,password))
            return

        return login, login

    security.declarePrivate('enumerateUsers')
    def enumerateUsers( self
                      , id=None
                      , login=None
                      , exact_match=False
                      , sort_by=None
                      , max_results=None
                      , **kw
                      ):
        """ See IUserEnumerationPlugin.
        """

        if not self.activated:return []
        service = self._sugarcrm()
        if isinstance( id, basestring ):
            id = [ str(id) ]

        if isinstance( login, basestring ):
            login = [ str(login) ]

        lookup_ids = []
        if login is not None and id is None:
            lookup_ids = login
        elif id is not None and login is None:
            lookup_ids = id

        res = {}
        for i in lookup_ids:
            if i in res.keys():
                continue
            if self.isInBlacklist(i):
                continue
            logger.info('enumerateUsers not cached %s'%i)
            res[i] = service.search(query_string=i, module='Users')

        user_info = []
        plugin_id = self.getId()
        e_url = '%s/manage_users' % plugin_id
        for i in res.keys():
            webinfo = res[i]
            if not webinfo:
                continue
            qs = 'user_id=%s' % i
            info = { 'id' : i
                      , 'login' : i
                      , 'pluginid' : plugin_id
                      , 'editurl' : '%s?%s' % (e_url, qs)
                   } 
            user_info.append(info)

        if len(user_info) == 0:
            for i in lookup_ids:
                self.addToBlacklist(i)

        return user_info

    security.declarePrivate('getPropertiesForUser')
    def getPropertiesForUser(self, user, request=None):
        """ See IPropertiesPlugin.
        """
        if not self.activated:return {}

        user_name = user.getUserName()

        service = self._sugarcrm()
        results = service.search(query_string=user_name, module='Users')
        properties = {}

        for result in results:
            if result['user_name'] == user_name:
                properties= {'email': str(result.get('email_address'))
                        , 'fullname': unicode(result.get('first_name')) + u' ' + unicode(result.get('last_name'))
                        }

        return properties

    def addToBlacklist(self, key):
        if not hasattr(self, '_v_blacklist_ids'):
            setattr(self, '_v_blacklist_ids', [])
        self._v_blacklist_ids.append(key)
    
    def isInBlacklist(self, key):
        if not hasattr(self, '_v_blacklist_ids'):
            setattr(self, '_v_blacklist_ids', [])
        return key in self._v_blacklist_ids


class AuthPlugin(SugarCRMPASPlugin, Cacheable):
    """Cacheable Version"""
    security = ClassSecurityInfo()

    security.declarePrivate('enumerateUsers')
    def enumerateUsers( self
                      , id=None
                      , login=None
                      , exact_match=False
                      , sort_by=None
                      , max_results=None
                      , **kw
                      ):

        if not self.activated:return []
        view_name = 'sugarcrmenumerateUsers'
        #logger.info('enumerateUsers cached')

        if isinstance( id, basestring ):
            id = [ str(id) ]

        if isinstance( login, basestring ):
            login = [ str(login) ]

        lookup_ids = []
        if login is not None and id is None:
            lookup_ids = login
        elif id is not None and login is None:
            lookup_ids = id

        # Look in the cache first...
        if len(lookup_ids)==0:
            return []

        keywords = {'id' : lookup_ids[0]}

        cached_info = self.ZCacheable_get( view_name=view_name
                                         , keywords=keywords
                                         , default="not_in_cache"
                                         )

        if cached_info != "not_in_cache":
            return tuple(cached_info)

        user_info = SugarCRMPASPlugin.enumerateUsers(self, id=id
                      , login=login
                      , exact_match=exact_match
                      , sort_by=sort_by
                      , max_results=max_results
                      , **kw
                      )

        self.ZCacheable_set(user_info,
                            view_name=view_name,
                            keywords=keywords)

        return tuple( user_info )

    security.declarePrivate('authenticateCredentials')
    def authenticateCredentials(self, credentials):
        """ See IAuthenticationPlugin.
        """
        if not self.activated:return
        #logger.info('authenticateCredentials cached')

        login = credentials.get('login')
        password = credentials.get('password')

        if not login or not password:
            return None

        utility = self._passord_utility()
        encrypted_password = utility.crypt(password)
        view_name = 'sugarcrmauthenticateCredentials'
        keywords = { 'login' : login, 'password' : password}

        cached_info = self.ZCacheable_get( view_name=view_name
                                         , keywords=keywords
                                         , default="not_in_cache"
                                         )
        if cached_info != "not_in_cache":
            return tuple(cached_info)

        logger.info('auth nothing in cache')
        res = SugarCRMPASPlugin.authenticateCredentials(self, credentials)
        self.ZCacheable_set(res, view_name=view_name, keywords=keywords)

        return res

    security.declarePrivate('getPropertiesForUser')
    def getPropertiesForUser(self, user, request=None):
        """ See IPropertiesPlugin.
        """

        if not self.activated:return {}
        user_name = str(user.getUserName())
        keywords = {'user_name':str(user_name)}
        view_name = 'sugarcrmgetPropertiesForUser'
        cached_properties = self.ZCacheable_get( view_name=view_name
                                         , keywords=keywords
                                         , default="not_in_cache"
                                         )
        if cached_properties != "not_in_cache":
            return cached_properties
        
        properties = SugarCRMPASPlugin.getPropertiesForUser(self, user,
                                                            request=request)

        self.ZCacheable_set(properties, view_name=view_name,
                            keywords=keywords)

        return properties
    #
    #   ZMI
    #
    manage_options = ( ( { 'label': 'Users', 
                           'action': 'manage_users', }
                         ,
                       )
                     + SugarCRMPASPlugin.manage_options
                     + Cacheable.manage_options
                     )

InitializeClass(AuthPlugin)

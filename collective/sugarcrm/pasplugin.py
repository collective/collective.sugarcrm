from Products.PluggableAuthService import plugins
from Products.PluggableAuthService import interfaces
from Products.PluggableAuthService import utils

from Globals import InitializeClass
from OFS.Cache import Cacheable

from zope import component
from zope import interface

from collective.sugarcrm.interfaces import IPasswordEncryption, ISugarCRM
from AccessControl import ClassSecurityInfo

class AuthPlugin(plugins.BasePlugin.BasePlugin):
    """This plugin try to authenticate the user
    with the login method of the sugarcrm webservice"""
    
    interface.implements(interfaces.plugins.IAuthenticationPlugin,
                         interfaces.plugins.IUserEnumerationPlugin,
                         interfaces.plugins.IPropertiesPlugin)

    meta_type = 'SugarCRM IAuthenticationPlugin'
    security = ClassSecurityInfo()
    
    def __init__(self, id, title=None):
        self.id = id
        self.title = title

    def _passord_utility(self):
        return component.getUtility(IPasswordEncryption)

    def _sugarcrm(self):
        return ISugarCRM(self)

    security.declarePrivate('authenticateCredentials')
    def authenticateCredentials(self, credentials):
        login = credentials.get('login')
        password = credentials.get('password')

        if not login or not password:
            return None

        utility = self._passord_utility()
        encrypted_password = utility.crypt(password)

        sugarcrm = self._sugarcrm()
        session = sugarcrm.login(login, encrypted_password)

        if session is None:
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
        return []

    security.declarePrivate('getPropertiesForUser')
    def getPropertiesForUser(self, user, request=None):
        return {}

InitializeClass(AuthPlugin)

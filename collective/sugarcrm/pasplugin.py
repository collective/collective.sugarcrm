from Products.PluggableAuthService import plugins
from Products.PluggableAuthService import interfaces
from Globals import InitializeClass
from OFS.Cache import Cacheable

from zope import component
from zope import interface

from collective.sugarcrm.interfaces import IPasswordEncryption, ISugarCRM
from AccessControl import ClassSecurityInfo


class AuthPlugin(plugins.BasePlugin.BasePlugin, Cacheable):
    """This plugin try to authenticate the user
    with the login method of the sugarcrm webservice"""
    
    interface.implements(interfaces.plugins.IAuthenticationPlugin)

    meta_type = 'SugarCRM IAuthenticationPlugin'
    security = ClassSecurityInfo()
    
    def __init__(self, id, title=None):
        self.id = self.id = id
        self.title = title

    security.declarePrivate('invalidateCacheForChangedUser')
    def invalidateCacheForChangedUser(self, user_id):
        pass

    security.declarePrivate('authenticateCredentials')
    def authenticateCredentials(self, credentials):
        login = credentials.get('login')
        password = credentials.get('password')

        if not login or not password:
            return None

        utility = component.getUtility(IPasswordEncryption)
        encrypted_password = utility.crypt(password)

        sugarcrm = ISugarCRM(self)
        try:
            session = sugarcrm.login(login, encrypted_password)
        except Exception, e:
            logger.info(e)
            return None

        if session.id == "-1":
            return None

        return login, login

InitializeClass(AuthPlugin)

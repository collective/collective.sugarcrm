from hashlib import md5

from collective.sugarcrm import interfaces
from zope import interface


class Password(object):
    """Password default encryption for sugarcrm"""
    interface.implements(interfaces.IPasswordEncryption)

    def crypt(self, password):
#        return base64.b64encode(md5.new(password).digest())
        m = md5()
        m.update(password)
        return m.hexdigest()

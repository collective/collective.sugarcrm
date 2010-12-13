from suds import WebFault

from zope import component
from zope import formlib
from zope import interface
from zope import schema

from zope.app.form.browser.textwidgets import ASCIIWidget

from plone.app.controlpanel.form import ControlPanelForm

from Products.CMFCore.interfaces import ISiteRoot
from Products.CMFCore.utils import getToolByName
from Products.CMFDefault.formlib.schema import ProxyFieldProperty
from Products.CMFDefault.formlib.schema import SchemaAdapterBase
from Products.CMFPlone.interfaces import IPloneSiteRoot
from Products.CMFPlone.utils import safe_hasattr
from Products.statusmessages.interfaces import IStatusMessage

from collective.sugarcrm import SugarCRMMessageFactory as _
from collective.sugarcrm import interfaces

class ISugarCRMSchema(interface.Interface):
    """Combined schema for the adapter lookup.
    """

    soap_url = schema.ASCIILine(title=_(u'label_soap_url',
                                default=u'SugarCRM SOAP URL'),
                        description=_(u'help_soap_url',
                                      default=u"Your SugarCRM SOAP v2 url: "
                              u"http://mysugardomain.com/service/v2/soap.php"),
                        required=True)

    soap_username = schema.ASCIILine(title=_(u'label_soap_userid',
                                     default=u"SOAP user login"),
                             description=_(u'help_soap_username',
                                           default=u"it will be used to"
                                   u"authenticate the portal actions done with"
                                   u"ISugarCRM component"),
                           required=True)

    soap_password = schema.Password(title=_(u'label_soap_pass',
                             default=u'SugarCRM SOAP password'),
                         required=False)

    activate_service = schema.Bool(title=_(u'label_activate_service',
                                   default=u'Activate WebService'),
                                   default=False)

    activate_pasplugin = schema.Bool(title=_(u'label_activate_pasplugin',
                                   default=u'Activate PAS Plugin (Authentication, User properties) '),
                                   default=False)

class SugarCRMControlPanelAdapter(SchemaAdapterBase):

    component.adapts(IPloneSiteRoot)
    interface.implements(ISugarCRMSchema)

    def __init__(self, context):
        super(SugarCRMControlPanelAdapter, self).__init__(context)
        self.context = getToolByName(context, 'portal_properties')

    def get_soap_url(self):
        return self.get('soap_url')

    def set_soap_url(self, value):
        self.set('soap_url', str(value))

    soap_url = property(get_soap_url, set_soap_url)

    def get_soap_pass(self):
        return str(self.get('soap_password'))

    def set_soap_pass(self, value):
        if type(value) in (unicode, str):
            self.set('soap_password', str(value))

    soap_password = property(get_soap_pass, set_soap_pass)

    def get_soap_username(self):
        return self.get('soap_username')

    def set_soap_username(self, value):
        self.set('soap_username', str(value))

    soap_username = property(get_soap_username, set_soap_username)

    def get_activate_service(self):
        return self.get('activate_service')

    def set_activate_service(self, value):
        return self.set('activate_service', bool(value))

    activate_service = property(get_activate_service, set_activate_service)

    def get_activate_pasplugin(self):
        return self.get('activate_pasplugin')

    def set_activate_pasplugin(self, value):
        if value:
            self.set_activate_service(True)
        return self.set('activate_pasplugin', bool(value))

    activate_pasplugin = property(get_activate_pasplugin,
                                  set_activate_pasplugin)

    def get(self, name):
        return getattr(self.context.sugarcrm,name)

    def set(self, name, value):
        if value and value != self.get(name):
            setattr(self.context.sugarcrm, name, value)

class SugarCRMControlPanel(ControlPanelForm):

    form_fields = formlib.form.FormFields(ISugarCRMSchema)
    #form_fields['email_from_address'].custom_widget = ASCIIWidget
    label = _("SugarCRM settings")
    description = _("SugarCRM settings for this site.")
    form_name = _("SugarCRM settings")

    def _on_save(self, data=None):
        password = data.get('soap_password', '')
        if type(password) not in (unicode, str) or not password:
            password = str(self.context.portal_properties.sugarcrm.soap_password)
        if not password or not data.get('activate_service', False):
            return

        sugarcrm = interfaces.ISugarCRM(self.context)
        utils = component.getUtility(interfaces.IPasswordEncryption)

        login = sugarcrm.login(str(data['soap_username']),
                               utils.crypt(password))
        if not login:
            message = _("Invalid credentials or URL.")
            IStatusMessage(self.request).addStatusMessage(message, type='error')

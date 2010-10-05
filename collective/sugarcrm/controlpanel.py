from zope.interface import Interface
from zope.component import adapts
from zope.component import getUtility
from zope.formlib import form
from zope.interface import implements
from zope.schema import Int
from zope.schema import Password
from zope.schema import TextLine
from zope.schema import ASCII
from zope.app.form.browser.textwidgets import ASCIIWidget

from Products.CMFCore.interfaces import ISiteRoot
from Products.CMFCore.utils import getToolByName
from Products.CMFDefault.formlib.schema import ProxyFieldProperty
from Products.CMFDefault.formlib.schema import SchemaAdapterBase
from Products.CMFPlone.interfaces import IPloneSiteRoot
from Products.CMFPlone.utils import safe_hasattr

from plone.app.controlpanel.form import ControlPanelForm

from collective.sugarcrm import SugarCRMMessageFactory as _
from collective.sugarcrm import interfaces
from suds import WebFault
from Products.statusmessages.interfaces import IStatusMessage

class ISugarCRMSchema(Interface):
    """Combined schema for the adapter lookup.
    """

    soap_url = TextLine(title=_(u'label_soap_url',
                                default=u'SugarCRM SOAP URL'),
                        description=_(u'help_soap_url',
                                      default=u"Your SugarCRM SOAP v2 url: "
                              u"http://mysugardomain.com/service/v2/soap.php"),
                        default=None,
                        required=True)

    soap_username = TextLine(title=_(u'label_soap_userid',
                                     default=u"SOAP user login"),
                             description=_(u'help_soap_username',
                                           default=u"it will be used to"
                                   u"authenticate the portal actions done with"
                                   u"ISugarCRM component"),
                           default=None,
                           required=True)

    soap_password = Password(title=_(u'label_soap_pass',
                             default=u'SugarCRM SOAP password'),
                         default=None,
                         required=False)

class SugarCRMControlPanelAdapter(SchemaAdapterBase):

    adapts(IPloneSiteRoot)
    implements(ISugarCRMSchema)

    def __init__(self, context):
        super(SugarCRMControlPanelAdapter, self).__init__(context)
        self.context = getToolByName(context, 'portal_properties')

    def get_soap_url(self):
        return self.get('soap_url')

    def set_soap_url(self, value):
        self.set('soap_url', value)

    soap_url = property(get_soap_url, set_soap_url)

    def get_soap_pass(self):
        return self.get('soap_password')

    def set_soap_pass(self, value):
        self.set('soap_password', value)

    soap_password = property(get_soap_pass, set_soap_pass)

    def get_soap_username(self):
        return self.get('soap_username')

    def set_soap_username(self, value):
        self.set('soap_username', value)

    soap_username = property(get_soap_username,
                             set_soap_username)

    def get(self, name):
        return getattr(self.context.sugarcrm,name)

    def set(self, name, value):
        if value and value != self.get(name):
            setattr(self.context.sugarcrm, name, value)

class SugarCRMControlPanel(ControlPanelForm):

    form_fields = form.FormFields(ISugarCRMSchema)
    #form_fields['email_from_address'].custom_widget = ASCIIWidget
    label = _("SugarCRM settings")
    description = _("SugarCRM settings for this site.")
    form_name = _("SugarCRM settings")

    def _on_save(self, data=None):

        if not 'soap_password' in data or not data['soap_password']:
            data['soap_password'] = self.context.portal_properties.sugarcrm.soap_password

        sugarcrm = interfaces.ISugarCRM(self.context)
        utils = getUtility(interfaces.IPasswordEncryption)

        try:
            login = sugarcrm.login(data['soap_username'],
                               utils.crypt(data['soap_password']))
        except WebFault, e:
            if e.fault.faultstring == "Invalid Login":
                message = _("Invalid credentials or URL.")
                IStatusMessage(self.request).addStatusMessage(message, type='error')

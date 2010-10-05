from collective.portlet.contact.interfaces import IPortletContactUtility
from collective.sugarcrm import interfaces
from zope import interface
from collective.portlet.contact.utils import encode_email
from Products.CMFCore.utils import getToolByName

class Contact(object):
    """collective.portlet.contact backend for sugarcrm Contacts module"""
    interface.implements(IPortletContactUtility)

    def search(self, context, q="", limit=10):
        """search within sugarcrm contacts"""
        sugarcrm = interfaces.ISugarCRM(context)
        results = sugarcrm.search(query_string=q,
                        module="Contacts", max=limit)
        item_str = "%(name)s - %(account_name)s|%(id)s"
        items = [item_str%item for item in results]

        return '\n'.join(items)

    def getContactInfos(self, context, uniq_id):
        """search within sugarcrm contacts"""

        urltool = getToolByName(context, 'portal_url')
        sugarcrm = interfaces.ISugarCRM(context)
        c = sugarcrm.get_entry(module="Contacts",uid=uniq_id)
        jpegurl = urltool() + '/@@ldapJpegPhoto?uid='+uniq_id

        return {'fullname': c['first_name'] +' '+ c['last_name'],
                'phonenumber': c['phone_work'],
                'mail': encode_email(c['email1'], c['email1']),
                'employeetype': c['title'],
                'uid': uniq_id,
                'photourl': ''}
        
contact = Contact()
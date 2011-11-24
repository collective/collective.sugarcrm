from collective.portlet.contact.interfaces import IPortletContactUtility
from collective.sugarcrm import interfaces
from zope import interface
from collective.portlet.contact.utils import encode_email
from Products.CMFCore.utils import getToolByName

class Contact(object):
    """Utility class for collective.portlet.contact backend. It use 
    'Contacts' module."""
    interface.implements(IPortletContactUtility)

    def search(self, context, q="", limit=10):
        """search within sugarcrm contacts"""

        sugarcrm = interfaces.ISugarCRM(context)
        results = sugarcrm.search(query_string=q,
                        module="Contacts", max=limit)

        items = []
        for item in results:
            if 'account_name' in item:
                item_str = "%(name)s - %(account_name)s|%(id)s"
            else:
                item_str = "%(name)s|%(id)s"
            items.append(item_str%item)

        return '\n'.join(items)

    def getContactInfos(self, context, uniq_id):
        """search within sugarcrm contacts"""

        urltool = getToolByName(context, 'portal_url')
        sugarcrm = interfaces.ISugarCRM(context)
        c = sugarcrm.get_entry(module="Contacts",id=uniq_id)

        if not c:
            return {'fullname': '',
                'phonenumber': '',
                'mail': '',
                'employeetype': '',
                'uid': uniq_id,
                'photourl': ''}

        jpegurl = urltool() + '/@@ldapJpegPhoto?uid='+uniq_id

        fullname = ' '.join((c.get('first_name','') or '',
                             c.get('last_name','') or '')).strip()

        return {'fullname': fullname,
                'phonenumber': c.get('phone_work',''),
                'mail': encode_email(c.get('email1',''), c.get('email1','')),
                'employeetype': c.get('title',''),
                'uid': uniq_id,
                'photourl': jpegurl}

contact = Contact()

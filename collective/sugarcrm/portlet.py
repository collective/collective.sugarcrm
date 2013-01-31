from zope import component
from zope import interface

from Products.CMFCore.utils import getToolByName

from collective.portlet.contact.addressbook import IAddressBook
from collective.sugarcrm import interfaces


class Contact(object):
    """Utility class for collective.portlet.contact backend. It use
    'Contacts' module."""
    interface.implements(IAddressBook)
    component.adapts(interface.Interface)

    def __init__(self, context):
        self.context = context

    def search(self, q="", limit=10):
        """search within sugarcrm contacts"""

        sugarcrm = interfaces.ISugarCRM(self.context)
        results = sugarcrm.search(query_string=q,
                        module="Contacts", max=limit)

        items = []
        for item in results:
            if 'account_name' in item:
                item_str = "%(name)s - %(account_name)s|%(id)s"
            else:
                item_str = "%(name)s|%(id)s"
            items.append(item_str % item)

        return '\n'.join(items)

    def getContactInfos(self, uniq_id):
        """search within sugarcrm contacts"""

        urltool = getToolByName(self.context, 'portal_url')
        sugarcrm = interfaces.ISugarCRM(self.context)
        c = sugarcrm.get_entry(module="Contacts", id=uniq_id)

        if not c:
            return {'fullname': '',
                'phonenumber': '',
                'mail': '',
                'employeetype': '',
                'uid': uniq_id,
                'photourl': ''}

        jpegurl = urltool() + '/@@ldapJpegPhoto?uid=' + uniq_id

        fullname = ' '.join((c.get('first_name', '') or '',
                             c.get('last_name', '') or '')).strip()
        email = c.get('email1', '')
        return {'fullname': fullname,
                'phonenumber': c.get('phone_work', ''),
                'mail': '<a href="mailto:%s">%s</a>' % (email, email),
                'employeetype': c.get('title', ''),
                'uid': uniq_id,
                'photourl': jpegurl}

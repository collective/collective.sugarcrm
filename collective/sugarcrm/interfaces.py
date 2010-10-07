from zope import interface

class ISugarCRM(interface.Interface):
    """SugarCRM webservice API"""

    def login(username, password):
        """authentication, return the session id"""

    def logout(session):
        """invalidate the provided session"""

    def get_entry(session=None, module_name="Contacts", id=""):
        """Return an entry defined by the id with all fields"""

    def search(session=None, query_string='', module='Contacts',offset=0,
                           max=None):
        """Search for entry from the specified module.
        By default, search for contacts"""
    
    def get_module_fields(session=None, module="Contacts"):
        """Return a list of fields description for the provided module
        
        a field:

           name = "id"
           type = "id"
           label = "ID:"
           required = 0
           options[] = <empty>

        """

class IComplexArgFactory(interface.Interface):
    """To create complex argument, just use this utility"""
    
    def create(argument_type):
        """create a complex argument for the current service"""

class IPasswordEncryption(interface.Interface):
    """Utility to crypt your password before use it with the WebService"""

    def crypt(password):
        """Return the encrypted password for the current service"""


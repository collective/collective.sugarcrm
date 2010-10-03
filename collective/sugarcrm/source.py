from zope import interface
from z3c.formwidget.query.interfaces import IQuerySource
from zope.schema.interfaces import IContextSourceBinder
from zope.schema.vocabulary import SimpleVocabulary
from zope.schema.vocabulary import SimpleTerm
from collective.sugarcrm.interfaces import ISugarCRM

class ContactQuerySource(object):
    """A query source based on a sugarcrm webservice
    """
    interface.implements(IQuerySource) #IVocabularyTokenized

    vocabulary = SimpleVocabulary(())
    sugarcrm_module = "Contacts"
    
    def __init__(self, context):
        self.context = context
        self.webservice = ISugarCRM(context)

    def __contains__(self, value):
        results = len(self.webservice.get_entry(uid=value, module=self.sugarcrm_module)) > 0
        return results

    def getTerm(self, value):

        try:
            results = self.webservice.get_entry(uid=value,
                                                module=self.sugarcrm_module)
            if not results:
                raise LookupError(value)
            term = self.buildTerm(results)
            return term
        except KeyError:
            raise LookupError(value)

    def buildTerm(self, entry):
        i = entry
        if i['first_name'] is None:
            name = i['last_name']
        elif i['last_name'] is None:
            name = i['first_name']
        else:
            name = i['first_name']+' '+i['last_name']
        return SimpleTerm(i['id'], i['id'], name)

    def getTermByToken(self, token):
        return self.getTerm(token)

    def __iter__(self):
        return iter([])

    def __len__(self):
        return 100

    def search(self, query_string):
        results = self.webservice.search(query_string=query_string,
                                         module=self.sugarcrm_module,
                                         max=25)
        terms = [self.buildTerm(i) for i in results]
        return SimpleVocabulary(terms)

class ContactSourceBinder(object):
    interface.implements(IContextSourceBinder)
    def __call__(self, context):
        return ContactQuerySource(context)

class AccountQuerySource(ContactQuerySource):
    
    sugarcrm_module = "Accounts"

    def buildTerm(self, entry):
        i = entry
        return SimpleTerm(i['id'], i['id'], i['name'])

class AccountSourceBinder(object):
    interface.implements(IContextSourceBinder)
    def __call__(self, context):
        return AccountQuerySource(context)

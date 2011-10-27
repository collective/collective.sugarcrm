from zope import interface
from z3c.formwidget.query.interfaces import IQuerySource
from zope.schema.interfaces import IContextSourceBinder
from zope.schema.vocabulary import SimpleVocabulary
from zope.schema.vocabulary import SimpleTerm
from collective.sugarcrm.interfaces import ISugarCRM
import logging
logger = logging.getLogger('collective.sugarcrm')


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

        contains = len(self.webservice.get_entry(id=value,
                                            module=self.sugarcrm_module)) > 0
        logger.debug('source.contains %s -> %s'%(value, contains))
        return contains

    def getTerm(self, value):

        entry = self.webservice.get_entry(id=value,
                                            module=self.sugarcrm_module)
        #I know, I'm suppose to raise LookupError, but it fails with
        #plone.formwidget.autocomplete (my only use case at the moment)
        if not entry:
            logger.error('source.getTerm: lookuperror of %s ->SimpleTerm'%value)
            return SimpleTerm(value, value, value)
            #raise LookupError(value)
        elif 'deleted' in entry.keys():
            if entry['deleted'] != "0":#default behaviour of sugarcrm
                logger.error('source.getTerm: lookuperror deleted returned\
                              for %s. %s'%(value, entry))
                return SimpleTerm(value, value, value)
                #raise LookupError(value)

        term = self.buildTerm(entry)
        logger.debug('source.getTerm(%s) -> %s'%(value, term.title))

        return term

    def buildTerm(self, entry):
        """build a term from a dict like object"""

        i = entry

        title = i.get('name','')
        if 'first_name' in i.keys() and 'last_name' in i.keys():
            title = ' '.join((i.get('first_name','') or '',
                              i.get('last_name','') or '')).strip()

        account_name = i.get('account_name','')
        if account_name:
            title += ' - '+account_name

        return SimpleTerm(i['id'], i['id'], title)

    def getTermByToken(self, token):

        logger.debug('source.getTermByToken')
        return self.getTerm(token)

    def __iter__(self):

        logger.debug('source.iter')
        return iter([])

    def __len__(self):

        logger.debug('source.len')
        return 100

    def search(self, query_string):
        
        is_id = len(query_string.split('-'))==5
        if is_id:
            term = self.getTerm(query_string)
            logger.debug("source.search(%s) -> %s"%(query_string, term.title))
            return SimpleVocabulary([term])

        results = self.webservice.search(query_string=query_string,
                                         module=self.sugarcrm_module,
                                         max=25)
        terms = [self.buildTerm(i) for i in results]

        logger.debug("source.search(%s) -> %s"%(query_string, len(terms)))
        return SimpleVocabulary(terms)

class ContactSourceBinder(object):
    interface.implements(IContextSourceBinder)
    def __call__(self, context):
#        return DummyQuerySource(context)
        return ContactQuerySource(context)

class AccountQuerySource(ContactQuerySource):

    sugarcrm_module = "Accounts"

    def buildTerm(self, entry):

        i = entry
        title = i.get('name','')

        if 'first_name' in i.keys() and 'last_name' in i.keys():
            title = ' '.join((i.get('first_name',''),
                             i.get('last_name',''))).strip()

        if 'billing_address_city' in i.keys():
            if i['billing_address_city']:
                title += ' - ' + i['billing_address_city']

        return SimpleTerm(i['id'], i['id'], title)


class AccountSourceBinder(object):
    interface.implements(IContextSourceBinder)
    def __call__(self, context):
        return AccountQuerySource(context)

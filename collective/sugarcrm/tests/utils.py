import os

SOAP = {
    'soap_url': os.getenv('SUGARCRM_SOAP_URL'),
    'soap_username': os.getenv('SUGARCRM_SOAP_USERNAME'),
    'soap_password': os.getenv('SUGARCRM_SOAP_PASSWORD'),
}
print SOAP

CONTACT = {'first_name': 'Jerald',
           'last_name': 'Arenas',
           'name': 'Jerald Arenas',
           'city': 'Cupertino'}

from ZPublisher.tests.testPublish import Request, Response


class FakeAcquisition(object):
    def __init__(self):
        self.aq_explicit = None


class FakeContext(object):

    def __init__(self):
        self.portal_type = 'News Item'
        self.id = "myid"
        self.title = "a title"
        self.description = "a description"
        self.creators = ["myself"]
        self.date = "a date"
        self.aq_inner = FakeAcquisition()
        self.aq_inner.aq_explicit = self
        self._modified = "modified date"
        self.messages = []

    def _old_generateNewId(self):
        return 'a-title'

    def getId(self):
        return self.id

    def Title(self):
        return self.title

    def Creators(self):
        return self.creators

    def Description(self):
        return self.description

    def Date(self):
        return self.date

    def modified(self):
        return self._modified

    def getPhysicalPath(self):
        return ('/', 'a', 'not', 'existing', 'path')

    def absolute_url(self):
        return "http://nohost.com/" + self.id

    def getRemoteUrl(self):  # fake Link
        return self.remoteUrl

    def plone_log(self, msg):
        self.messages.append(msg)


class FakeImage(object):
    def __init__(self):
        self.data = 'photo'


class FakePortal(FakeContext):

    def __init__(self):
        self.data = {'images/uniq_id': FakeImage()}

    def unrestrictedTraverse(self, key):
        return self.data[key]


class FakeSettings(object):
    def __init__(self):
        self.backend = "test"
        self.ajax = False
        self.dummy_fullname = "Foo Bar"
        self.dummy_phone = "+33 (0) 111 222 333"
        self.dummy_mail = "foo@bar.co"
        self.dummy_employee_type = "Developer"
        photo = "++resource++collective-portlet-contact/defaultUser.png"
        self.dummy_photo_url = photo
        #get_properties stuff
        self.photo_storage = 'ofs'
        self.default_photo_path = ''
        self.photo_ofs_directory = 'images'
        self.photo_cache_maxage = ''

    def __getitem__(self, key):
        return getattr(self, key)


class FakeBackend(object):
    def __init__(self):
        self.contacts = {}

    def search(self, q="", limit=10):
        return self.contacts.values()

    def getContactInfos(self, uniq_id):
        return self.contacts[uniq_id]


class RequestWithGet(Request):

    def __init__(self):
        Request.__init__(self)
        self.form = {}
        self.response = ResponseWithSet()

    def get(self, a, b=''):
        return self.form.get(a, b)


class ResponseWithSet(Response):

    def __init__(self):
        self.headers = {}
        self.content = ""

    def setHeader(self, key, value):
        self.headers[key] = value

    def write(self, content):
        self.content += content

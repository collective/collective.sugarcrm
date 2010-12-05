import os

SOAP = {'soap_url':os.getenv('SUGARCRM_SOAP_URL',
                 'http://trial.sugarcrm.com/ncxupk6372/service/v2/soap.php'),
'soap_username':os.getenv('SUGARCRM_SOAP_USERNAME','will'),
'soap_password':os.getenv('SUGARCRM_SOAP_PASSWORD','will'),
}

CONTACT = {'first_name':'Jerald',
           'last_name': 'Arenas',
           'name':      'Jerald Arenas',
           'city':      'Cupertino'}



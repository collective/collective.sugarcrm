from zope.i18nmessageid.message import MessageFactory
  # -*- extra stuff goes here -*- 

SugarCRMMessageFactory = MessageFactory("collective.sugarcrm")

def initialize(context):
    """Initializer called when used as a Zope 2 product."""

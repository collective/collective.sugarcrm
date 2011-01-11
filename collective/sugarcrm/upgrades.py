
def upgrade_1_to_2(context):
    setup = getToolByName(context, "portal_setup")
    setup.runImportStepFromProfile(
        'profile-collective.sugarcrm:default',
        'controlpanel',
        purge_old=False)


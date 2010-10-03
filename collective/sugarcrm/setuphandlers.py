from collective.sugarcrm import pasplugin as plugin

plugin_id = "sugarcrm"
plugin_title = plugin.AuthPlugin.meta_type

def setupPasPlugin(context):
    if context.readDataFile('sugarcrm.txt') is None:
        return

    portal = context.getSite()

    pas = portal.acl_users

    if not plugin_id in pas.objectIds():
        manager = plugin.AuthPlugin(plugin_id, plugin_title)
        pas._setObject(plugin_id, manager)
        provider = pas[plugin_id]
        provider.manage_activateInterfaces(['IAuthenticationPlugin'])

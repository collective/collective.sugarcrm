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
    provider.manage_activateInterfaces(['IAuthenticationPlugin',
                                        'IUserEnumerationPlugin',
                                        'IPropertiesPlugin'])

    #because default plone properties plugin mask any other, 
    #you must place it before it
    iface = pas.plugins._getInterfaceFromName('IPropertiesPlugin')
    pluginids = pas.plugins.listPluginIds(iface)
    plugin_index = pluginids.index(plugin_id)
    for i in range(plugin_index):
        pas.plugins.movePluginsUp(iface, [plugin_id])

    #set _activated var to None to reactivate pas plugin
    provider._activated = None

def uninstallPasPlugin(context):
    if context.readDataFile('sugarcrm.txt') is None:
        return

    portal = context.getSite()
    pas = portal.acl_users
    if plugin_id in pas.objectIds():
        pas[plugin_id].manage_activateInterfaces([])
        pas.manage_delObjects([plugin_id])

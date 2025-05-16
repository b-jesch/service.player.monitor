import xbmc
import xbmcgui
import xbmcaddon
import xbmcvfs

import json
import os

addon = xbmcaddon.Addon()
addon_id = addon.getAddonInfo('id')
addon_name = addon.getAddonInfo('name')
addon_version = addon.getAddonInfo('version')
log_path = os.path.join(xbmcvfs.translatePath(addon.getAddonInfo('profile')), 'log')

def getNextLogfileName(path):
    # determine next log file name
    subversion = 1
    while True:
        log_file = os.path.join(path, 'monitor.log.%s' % str(subversion))
        if not xbmcvfs.exists(log_file): return log_file
        subversion = (subversion + 1)

def setProp(key, value):
    xbmcgui.Window(10000).setProperty(str(key), str(value))

def getProp(key):
    if xbmcgui.Window(10000).getProperty(key) == '': return None
    elif xbmcgui.Window(10000).getProperty(key).lower() == 'true': return True
    elif xbmcgui.Window(10000).getProperty(key).lower() == 'false': return False
    return xbmcgui.Window(10000).getProperty(key)

def clearProp(key):
    xbmcgui.Window(10000).clearProperty(key)


def jsonrpc(query):
    querystring = {"jsonrpc": "2.0", "id": 1}
    querystring.update(query)
    return json.loads(xbmc.executeJSONRPC(json.dumps(querystring)))

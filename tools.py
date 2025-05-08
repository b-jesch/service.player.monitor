import xbmc
import xbmcgui
import json

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

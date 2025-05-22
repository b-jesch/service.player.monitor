from tools import *

menu_list =['Interrupt Monitoring', 'Show Protocol', 'Delete all Protocol Files', 'Exit']
menu = xbmcgui.Dialog().select(addon_name, menu_list)
if menu == 0:
    if not getProp('player.monitor.run') or getProp('player.monitor.run') is None:
        xbmcgui.Dialog().notification(addon_name, 'Monitoring interrupted by User')

    setProp('player.monitor.run', 'True')

elif menu == 1:
    browser = xbmcgui.Dialog().browse(1, addon_name, 'files', '',False,
                                      False, defaultt=log_path)
    if browser != log_path and browser != '':
        with open(browser, 'r') as f: content = f.read()
        xbmcgui.Dialog().textviewer(addon_name, content, usemono=True)

elif menu == 2:
    dirs, files = xbmcvfs.listdir(log_path)
    if len(files) > 0:
        for file in files: xbmcvfs.delete(os.path.join(log_path, file))
        xbmcgui.Dialog().notification(addon_name, 'All Protocol Files deleted')
        setProp('player.monitor.log', 'True')

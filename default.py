import xbmc
import xbmcaddon
import xbmcvfs
import os
from datetime import datetime

addon = xbmcaddon.Addon()
addon_id = addon.getAddonInfo('id')
addon_version = addon.getAddonInfo('version')
log_path = xbmcvfs.translatePath(addon.getAddonInfo('profile'))

if not xbmcvfs.exists(log_path): xbmcvfs.mkdirs(log_path)

# determine next log file name
subversion = 1
while 0 < subversion < 100:
    log_file = os.path.join(log_path, 'monitor.log.%s' % str(subversion))
    if not xbmcvfs.exists(log_file): break
    subversion = (subversion + 1) % 100


class NotificationLogger(object):
    def __init__(self):
        self.repeats = 0
        self.lastMsg = None
        self.logFile = log_file

    def file_logger(self, msg):
        with open(self.logFile, 'a') as file: file.write(datetime.now().strftime('%d.%m.%Y %H:%M:%S') + ': ' + msg + "\n")
        file.close()

    def log(self, msg, level=xbmc.LOGINFO, writeout=True):
        if self.lastMsg != msg:
            if self.repeats > 0:
                xbmc.log('[%s %s] last message repeated %s times' % (addon_id, addon_version, self.repeats), level=level)
                self.repeats = 0
            xbmc.log('[%s %s] %s' % (addon_id, addon_version, msg), level=level)
            if writeout: self.file_logger(msg)
        else:
            self.repeats += 1
        self.lastMsg = msg

NL = NotificationLogger()


class EventLogger(xbmc.Monitor):
    def __init__(self):
        xbmc.Monitor.__init__(self)
        NL.log('Event logger started')
        NL.log('Logging into %s' % log_file, writeout=False)


    def onNotification(self, sender, method, data):
        if method == 'Player.OnPlay': NL.log('Player started: %s' % data)
        elif method == 'Player.OnPause': NL.log('Player paused: %s' % data)
        elif method == 'Player.OnResume': NL.log('Player resumed: %s' % data)
        elif method == 'Player.OnStop': NL.log('Player stopped: %s' % data)
        else: NL.log('Event discarded: %s' % method, writeout=False)


    def logEvents(self):
        while not self.abortRequested(): self.waitForAbort(1000)
        NL.log('Event logger stopped')


if __name__ == '__main__':
    Logger = EventLogger()
    Logger.logEvents()
    del Logger

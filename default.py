from tools import *
from datetime import datetime

if not xbmcvfs.exists(log_path): xbmcvfs.mkdirs(log_path)

player = xbmc.Player


class NotificationLogger(object):
    def __init__(self):
        self.repeats = 0
        self.lastMsg = None
        self.logFile = getNextLogfileName(log_path)

    def file_logger(self, msg):
        if getProp('player.monitor.log') is not None and getProp('player.monitor.log'):
            self.logFile = getNextLogfileName(log_path)
            clearProp(getProp('player.monitor.log'))

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
        self.lastPlayed = None
        self.attemptsToStart = 0
        self.givenUp = False
        clearProp('player.monitor.run')

        NL.log('Event logger started')
        NL.log('Logging into %s' % log_file, writeout=False)

    def resetPlayerStates(self, message):
        self.attemptsToStart = 1
        self.givenUp = False
        NL.log(message)

    def getPlayerProps(self, data):
        res = json.loads(data)
        if res.get('item', None) is not None: return res['item']
        return None

    def onNotification(self, sender, method, data):
        if method == 'Player.OnPlay':
            self.lastPlayed = self.getPlayerProps(data)
            xbmc.sleep(2000)
            if xbmc.getCondVisibility('Player.Playing'): self.resetPlayerStates('Player started: %s' % data)
            clearProp('player.monitor.run')

        elif method == 'Player.OnPause': NL.log('Player paused: %s' % data)
        elif method == 'Player.OnResume': NL.log('Player resumed: %s' % data)

        elif method == 'Player.OnStop':
            self.lastPlayed = self.getPlayerProps(data)
            NL.log('Player stopped: %s' % data)
            self.playerRestart()

        else: NL.log('Event discarded: %s' % method, writeout=False)

    def playerRestart(self):
        self.waitForAbort(30)
        if self.abortRequested() or self.givenUp: return
        if getProp('player.monitor.run') is not None and getProp('player.monitor.run'):
            self.lastPlayed = None
            NL.log('Player Monitoring interrupted by User')

        if not xbmc.getCondVisibility('Player.Playing') and self.lastPlayed is not None and self.lastPlayed.get('id', None) is not None:
            if self.attemptsToStart < 4:
                query = {'method': 'Player.Open', 'params': {'item': {'channelid': self.lastPlayed['id']}}}
                res = jsonrpc(query)
                xbmc.sleep(2000)

                if 'result' in res and res['result'] == 'OK' and xbmc.getCondVisibility('Player.Playing'):
                    self.resetPlayerStates('Player successfully reopened: %s' % self.lastPlayed.get('title', 'unknown'))
                    return

                elif 'result' in res and res['result'] == 'OK' and not xbmc.getCondVisibility('Player.Playing'):
                    NL.log('Player (re)opened %s time(s): %s but did\'nt play yet' % (self.attemptsToStart, self.lastPlayed.get('title', 'unknown')))

                else:
                    NL.log('Could not open Channel: %s' % self.lastPlayed.get('title', 'unknown'))

                if not self.givenUp:
                    NL.log('%s attempts restarting player on channel %s, giving up' % (self.attemptsToStart, self.lastPlayed.get('title', 'unknown')))
                    self.givenUp = True
            else:
                self.attemptsToStart += 1

    def logEvents(self):
        while not self.abortRequested():
            self.waitForAbort(60)

        NL.log('Event logger stopped')


if __name__ == '__main__':
    Logger = EventLogger()
    Logger.logEvents()
    clearProp('player.monitor.run')
    del Logger

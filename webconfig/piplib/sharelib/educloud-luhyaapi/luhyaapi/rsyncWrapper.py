# coding=UTF-8

import pexpect
import multiprocessing, threading

# client: /opt/luhya/images/imageID/machine, attributes.conf
# server: /var/www/images/imageID/machine, attributes.conf
# typical user case:
#    1.  client initiate copying file from server to client
#        rsync -r -P rsync://serverIP/luhya/imageID  /opt/luhya/images/
#    2.  server initiate copying file from server to client
#        rsync -r -P /var/www/images/imageID  rsync://clientIP/luhya/
class rsyncWrapper():
    def __init__(self, source, destination):
        self._src = source
        self._dest = destination
        self._whole = " -r -P -p "

    def startRsync(self, ):
        cmd_line = "rsync " + self._whole + self._src + " " + self._dest
        cmds = cmd_line.split()
        self._proc = pexpect.spawn(cmd_line)

    def isRsyncLive(self):
        return self._proc.isalive()

    def getExitStatus(self):
        return self._proc.status

    def returnZeroProgress(self):
        return "0", "0%", "0.00kB/s", "0:00:00"

    def getProgress(self, ):
        try:
            if self.isRsyncLive():
                progress = self._proc.readline()

                progs = progress.split()
                if 'luhya' in progs[0]:
                    #      161696          4%  233.21MB/s    0:01:03
                    return progs[1], progs[2], progs[3],     progs[4]
                else:
                    #       0    0%    0.00kB/s    0:00:00
                    return self.returnZeroProgress()

            else:
                return self.returnZeroProgress()
        except:
            return self.returnZeroProgress()

class rsyncWorkerThread(threading.Thread):
    def __init__(self, logger, src, dst):
        threading.Thread.__init__(self)

        self.src        = src
        self.dst        = dst
        self.progress   = 0
        self.failed     = 0
        self.done       = 0
        self.errormsg   = ''
        self.logger     = logger

    def isFailed(self):
        return self.failed

    def isDone(self):
        return self.done

    def getprogress(self):
        return self.progress

    def getErrorMsg(self):
        return self.errormsg

    def run(self):
        self.logger.error("rsyncWorkerThread is running ... ...")
        self.logger.error('src=%s, dst=%s' % (self.src, self.dst))

        self.progress = 0

        rsync = rsyncWrapper(self.src, self.dst)
        rsync.startRsync()

        while rsync.isRsyncLive():
            tmpfilesize, pct, bitrate, remain = rsync.getProgress()
            msg = "%s  %s %s %s" % (tmpfilesize, pct, bitrate, remain)
            # self.logger.error(msg)
            self.progress = int(pct.split('%')[0])

        exit_code = rsync.getExitStatus()
        if exit_code == 0:
            self.progress == 100 # success
            self.failed     = 0
            self.errormsg   = "process exit with code=%s, progress=%s" % ( 0, 100)
            self.done       = 1
        else:
            self.failed   = 1
            self.errormsg = "process exit with code=%s, progress=%s" % ( exit_code, self.progress)
        self.logger.error(self.errormsg)


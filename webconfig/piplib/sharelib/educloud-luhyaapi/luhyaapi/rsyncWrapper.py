# coding=UTF-8

import pexpect

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


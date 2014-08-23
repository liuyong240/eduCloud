from luhyaapi.rsyncWrapper import *

# second to sync to server
source = "rsync://192.168.56.101/luhya/xp"
destination = "/storage/images/"
rsync = rsyncWrapper(source, destination)
rsync.startRsync()

while rsync.isRsyncLive():
    tmpfilesize, pct, bitrate, remain = rsync.getProgress()
    msg = "%s  %s %s %s" % (tmpfilesize, pct, bitrate, remain)
    ratio = int(pct.split('%')[0])
    print msg

exit_code = rsync.getExitStatus()
print exit_code



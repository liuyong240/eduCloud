import memcache
import json
import time

mc = memcache.Client(['127.0.0.1:11211'], debug=0)
tid="xp:IMGabcd:INS1234"
payload = {
		'type'      : 'taskstatus',
		'phase'     : "downloading",
		'progress'  : 0,
		'tid'       : tid
}

index = 0;
while index <= 100:
	mc.set(tid, payload)
	index = index + 1
	payload['progress'] = index
	print payload
	time.sleep(0.1)

payload['progress'] = -100
mc.set(tid, payload)






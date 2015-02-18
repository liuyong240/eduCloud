from luhyaapi.hostTools import *
import time

payload = {}
index = 0
while True:

    try:
        payload['service_data'] = getServiceStatus('nc')
    except Exception as e:
        print "getServiceStatus:" + str(e)

    try:
        payload['hardware_data']    = getHostHardware()
    except Exception as e:
        print "getHostHardware:" + str(e)

    try:
        payload['net_data']         = getHostNetInfo()
    except Exception as e:
        print "getHostNetInfo:" + str(e)

    try:
        payload['vm_data']          = getVMlist()
    except Exception as e:
        print "getVMlist:" + str(e)

    # time.sleep(3)
    print "Times: %s" % index
    # print payload
    index += 1
    payload = {}




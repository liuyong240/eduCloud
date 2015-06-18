import os, commands

def get_immediate_subdirectories(a_dir):
    return [name for name in os.listdir(a_dir)
            if os.path.isdir(os.path.join(a_dir, name))]

def registerVDI(root_dir):
    existing_vms = get_immediate_subdirectories(root_dir)
    for vm in existing_vms:
        if vm in list_vms:
            continue
        else:
            # get this vm's snapshot vdi file and order in size
            snap_dir = '%s/%s/Snapshots/' % (root_dir, vm)
            snap_vdis = os.listdir(snap_dir)
            if len(snap_vdis) == 2:
                size0 = os.path.getsize(snap_dir + snap_vdis[0])
                size1 = os.path.getsize(snap_dir + snap_vdis[1])
                if size0 > size1:
                    cmd = "vboxmanage showhdinfo %s" % (snap_dir + snap_vdis[1])
                    commands.getoutput(cmd)
                    cmd = "vboxmanage showhdinfo %s" % (snap_dir + snap_vdis[0])
                    commands.getoutput(cmd)
                else:
                    cmd = "vboxmanage showhdinfo %s" % (snap_dir + snap_vdis[0])
                    commands.getoutput(cmd)
                    cmd = "vboxmanage showhdinfo %s" % (snap_dir + snap_vdis[1])
                    commands.getoutput(cmd)

                # now re-register this vm
                vbox_file = "%s/%s/%s.vbox" % (root_dir, vm, vm)
                cmd = "vboxmanage registervm %s" % vbox_file
                out = commands.getoutput(cmd)
                print "cmd=%s" % cmd
                print "out=%s" % out
            else:
                print "-------------------------------------------------------------"
                print "Error:"
                print "  There are more than 2 vdi file in Snapshot : %s" % snap_dir
                print "-------------------------------------------------------------"


# unregister all inaccessible vms
is_inaccessible = False

cmd = "vboxmanage list vms"
out = commands.getoutput(cmd)
list_vms = [];
if len(out) > 0:
    vms = out.split()
    num_of_vms = len(vms)/2
    for x in range(0, num_of_vms):
        vm = {}
        vm['insid'] = vms[2*x].replace('"', '')
        vm['uuid'] = vms[2*x+1].replace('{', '').replace('}', '')

        if 'inaccessible' in vm['insid']:
            is_inaccessible = True
            cmd = "vboxmanage unregistervm %s" % vm['uuid']
            out = commands.getoutput(cmd)
        else:
            list_vms.append(vm['insid'])

if is_inaccessible:
    print "Find inaccessible VM, try to recover it ... ..."
    # vboxmanager showhdinfo on all /storage/images/
    avail_images = get_immediate_subdirectories('/storage/images/')
    for img in avail_images:
        mfile = '/storage/images/%s/machine' % img
        if os.path.exists(mfile):
            cmd = "vboxmanage showhdinfo %s" % mfile
            commands.getoutput(cmd)

    registerVDI("/storage/VMs")
    registerVDI("/storage/tmp/VMs")
else:
    print "No inaccessible VM, gracefully exit."


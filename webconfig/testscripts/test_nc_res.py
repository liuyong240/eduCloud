VALID_NC_RES = {
    'server': {
        'cpu_usage'     : 10,
        'cpu'           : 2,
        'disk'          : 20,
        'mem'           : 2,
    },

    'desktop': {
        'cpu_usage'     : 20,
        'cpu'           : 1,
        'disk'          : 10,
        'mem'           : 2,
    }
}

while 1:
    vm_res_matrix = VALID_NC_RES['desktop'].copy()
    vm_res_matrix['mem'] += 2

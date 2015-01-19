from sortedcontainers import SortedList

nc1    = {
        '3cpu'       : 1,
        '2cpu_usage' : 10,
        '1mem'       : 10,
        '4disk'      : 200,
    }
nc2    = {
        '3cpu'       : 3,
        '2cpu_usage' : 90,
        '1mem'       : 5,
        '4disk'      : 100,
    }
nc3    = {
        '3cpu'       : 10,
        '2cpu_usage' : 80,
        '1mem'       : 15,
        '4disk'      : 50,
    }

l = SortedList()
l.add(nc1)
l.add(nc2)
l.add(nc3)

length = len(l)

for index in range(0, len(l)):
    print l[length - index -1]

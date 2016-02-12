#!/usr/bin/env python

import sys,os

if len(sys.argv) != 2:
    print "NOPE: Call this with one integer argument > 0, the number of times to repeat the process"
    quit()

assert len(sys.argv) == 2
x = int(sys.argv[1])
assert x > 0

cmd = "(python pagerank_map.py < input.txt | sort > tmpA.txt && python pagerank_reduce.py < tmpA.txt > tmpB.txt && python process_map.py < tmpB.txt | sort > tmpA.txt && python process_reduce.py < tmpA.txt"
cmd += (x - 1) * " > tmpB.txt && python pagerank_map.py < tmpB.txt | sort > tmpA.txt && python pagerank_reduce.py < tmpA.txt > tmpB.txt && python process_map.py < tmpB.txt | sort > tmpA.txt && python process_reduce.py < tmpA.txt"
cmd += " && rm tmpA.txt tmpB.txt ) || (cat tmpB.txt && rm tmpA.txt tmpB.txt)"

os.system(cmd)

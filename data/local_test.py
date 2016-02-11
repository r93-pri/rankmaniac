#!/usr/bin/env python

import sys,os

if len(sys.argv) != 2:
    print "NOPE: Call this with one integer argument > 0, the number of times to repeat the process"
    quit()

assert len(sys.argv) == 2
x = int(sys.argv[1])
assert x > 0

cmd = "python pagerank_map.py < input.txt | sort | python pagerank_reduce.py"
cmd += (x - 1) * " | python pagerank_map.py | sort | python pagerank_reduce.py"
cmd += " | python process_map.py | sort | python process_reduce.py"

os.system(cmd)

#!/usr/bin/env python

import sys
from collections import namedtuple

ALPHA = 0.85 # damping factor
Line = namedtuple('Line', 'node_num iter_num pr prev_pr connected_nodes incoming_pr')

def parse_line(line):
    l = line.strip().split("\t")
    assert len(l) >= 2
    key = l[0]
    value = l[1]
    assert key.startswith("NodeId:")
    node_num = int(key[7:])
    if not value.startswith("i"):  #First iteration!
        value = "i0," + value   # On the first iteration we add an iteration marker
    value = value.split(",")
    iter_num = int(value[0][1:])
    pr = float(value[1])
    prev_pr = float(value[2])
    connected_nodes = map(int, value[3:]) if len(value) > 3 else []
    if len(l) == 3:
        incoming_pr = map(float, l[2].split(","))
    else:
        incoming_pr = []

    return Line(node_num, iter_num, pr, prev_pr, connected_nodes, incoming_pr)

def stringify_Line(l):
    output = "NodeId:" + str(l.node_num) + "\t"
    output += "i" + str(l.iter_num) + "," + str(l.pr) + "," + str(l.prev_pr)
    if len(l.connected_nodes) > 0:
        output += "," + (','.join(map(str, l.connected_nodes)))
    output += "\n"
    return output

# compute new pagerank by summing pagerank/degree of incoming links
def reduce_pr(l):
    new_pr = (1 - ALPHA) + ALPHA * sum(l.incoming_pr)
    l = l._replace(prev_pr=(l.pr))
    l = l._replace(pr=(new_pr))
    return l
    

#
# This program simply represents the identity function.
#

line = sys.stdin.readline()
if line.startswith("FinalRank"):
    sys.stdout.write(line)
    for line in sys.stdin:
        sys.stdout.write(line)
    sys.exit()
else:
    l = parse_line(line)
    l = reduce_pr(l)
    sys.stdout.write(stringify_Line(l))

for line in sys.stdin:
    l = parse_line(line)
    l = reduce_pr(l)
    sys.stdout.write(stringify_Line(l))

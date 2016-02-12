#!/usr/bin/env python

import sys
from collections import namedtuple

ALPHA = 0.85 # damping factor
Line = namedtuple('Line', 'node_num iter_num rank pr prev_pr connected_nodes')

ranks = {}
nodes = []

def parse_line(line):
    l = line.strip().split("\t")
    assert len(l) >= 2
    key = l[0]
    value = l[1]
    assert key.startswith("NodeId:")
    node_num = int(key[7:])
    value = value.split(",")
    if len(value) == 1:
        if not node_num in ranks:
            ranks[node_num] = 0
        ranks[node_num] += float(value[0])
    else:
        # I'm putting this here so that I dont have to check it in reduce_pr()
        # If I put it here, it does this check n times total. Otherwise, it does it 2n times total.
        if not node_num in ranks:
            ranks[node_num] = 0
        iter_num = int(value[0][1:])
        rank = int(value[1][1:])
        pr = float(value[2])
        prev_pr = float(value[3])
        connected_nodes = map(int, value[4:]) if len(value) > 3 else []
        if len(l) == 3:
            incoming_pr = map(float, l[2].split(","))
        else:
            incoming_pr = []

        nodes.append(Line(node_num, iter_num, rank, pr, prev_pr, connected_nodes))

def stringify_Line(l):
    output = "NodeId:" + str(l.node_num) + "\t"
    output += "i" + str(l.iter_num) + ",r" + str(l.rank) + "," + str(l.pr) + "," + str(l.prev_pr)
    if len(l.connected_nodes) > 0:
        output += "," + (','.join(map(str, l.connected_nodes)))
    output += "\n"
    return output

# compute new pagerank by summing pagerank/degree of incoming links
def reduce_pr(l):
    new_pr = (1 - ALPHA) + ALPHA * ranks[l.node_num]
    l = l._replace(prev_pr=(l.pr))
    l = l._replace(pr=(new_pr))
    return l


for line in sys.stdin:
    parse_line(line)

for l in nodes:
    l = reduce_pr(l)
    sys.stdout.write(stringify_Line(l))

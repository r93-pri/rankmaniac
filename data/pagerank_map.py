#!/usr/bin/env python

import sys

from collections import namedtuple

Line = namedtuple('Line', 'node_num iter_num pr prev_pr connected_nodes')
intermediates = {}

def parse_line(line):
    l = line.strip().split("\t")
    assert len(l) == 2
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
    return Line(node_num, iter_num, pr, prev_pr, connected_nodes)

def stringify_Line(l, incoming_pr):
    output = "NodeId:" + str(l.node_num) + "\t"
    output += "i" + str(l.iter_num) + "," + str(l.pr) + "," + str(l.prev_pr)
    if len(l.connected_nodes) > 0:
        output += "," + (','.join(map(str, l.connected_nodes)))
    output += "\t"
    if len(incoming_pr) > 0:
        output += ','.join(map(str, incoming_pr))
    output += "\n"
    return output

def map_pr(l):
    if len(l.connected_nodes) == 0:
        if l.node_num in intermediates:
            intermediates[l.node_num].append(l.pr)
        else:
            intermediates[l.node_num] = [l.pr]

    for node in l.connected_nodes:
        # collect pageranks of incoming links
        if node in intermediates:
            intermediates[node].append(l.pr / len(l.connected_nodes))
        else:
            intermediates[node] = [l.pr / len(l.connected_nodes)]


#
# This program simply represents the identity function.
#
lines = []
line = sys.stdin.readline()
if line.startswith("FinalRank"):
    sys.stdout.write(line)
    for line in sys.stdin:
        sys.stdout.write(line)
    sys.exit()
else:
    l = parse_line(line)
    l = l._replace(iter_num=(l.iter_num + 1))  # We increment the number of iterations each time
    map_pr(l) # add node's pagerank / degree to each page it links to
    lines.append(l)

for line in sys.stdin:
    l = parse_line(line)
    l = l._replace(iter_num=(l.iter_num + 1))  # We increment the number of iterations each time
    map_pr(l) # add node's pagerank / degree to each page it links to
    lines.append(l)

for l in lines:
    incoming_pr = intermediates[l.node_num] if l.node_num in intermediates else []
    sys.stdout.write(stringify_Line(l, incoming_pr))

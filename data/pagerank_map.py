#!/usr/bin/env python

import sys

from collections import namedtuple

Line = namedtuple('Line', 'node_num iter_num rank pr prev_pr connected_nodes')

def parse_line(line):
    l = line.strip().split("\t")
    assert len(l) == 2
    key = l[0]
    value = l[1]
    assert key.startswith("NodeId:")
    node_num = int(key[7:])
    if not value.startswith("i"):  #First iteration!
        value = "i0,r-1," + value   # On the first iteration we add an iteration marker and an initial rank
    value = value.split(",")
    iter_num = int(value[0][1:])
    rank = int(value[1][1:])
    pr = float(value[2])
    prev_pr = float(value[3])
    connected_nodes = map(int, value[4:]) if len(value) > 3 else []
    return Line(node_num, iter_num, rank, pr, prev_pr, connected_nodes)

def stringify_Line(l):
    output = "NodeId:" + str(l.node_num) + "\t"
    output += "i" + str(l.iter_num) + ",r" + str(l.rank) + "," + str(l.pr) + "," + str(l.prev_pr)
    if len(l.connected_nodes) > 0:
        output += "," + (','.join(map(str, l.connected_nodes)))
    output += "\n"
    return output

def map_pr(l):
    if len(l.connected_nodes) == 0:
        emission = "NodeId:" + str(l.node_num) + "\t" + str(l.pr) + "\n"
        sys.stdout.write(emission)

    for node in l.connected_nodes:
        # collect pageranks of incoming links
        emission = "NodeId:" + str(node) + "\t" + str(l.pr / len(l.connected_nodes)) + "\n"
        sys.stdout.write(emission)


lines = []
line = sys.stdin.readline()
if line.startswith("FinalRank"):
    sys.stdout.write(line)
    for line in sys.stdin:
        sys.stdout.write(line)
    sys.exit()

l = parse_line(line)
l = l._replace(iter_num=(l.iter_num + 1))  # We increment the number of iterations each time
map_pr(l) # add node's pagerank / degree to each page it links to
sys.stdout.write(stringify_Line(l))

for line in sys.stdin:
    l = parse_line(line)
    l = l._replace(iter_num=(l.iter_num + 1))  # We increment the number of iterations each time
    map_pr(l) # add node's pagerank / degree to each page it links to
    sys.stdout.write(stringify_Line(l))

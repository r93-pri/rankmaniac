#!/usr/bin/env python

import sys

from collections import namedtuple

Line = namedtuple('Line', 'node_num iter_num pr prev_pr connected_nodes')

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


#
# This program simply represents the identity function.
#
final_output = []
for line in sys.stdin:
    l = parse_line(line)
    final_output.append(l)

# sort in descending order by pagerank
final_output = sorted(final_output, key=lambda line: line.pr, reverse=True)

for l in final_output[:20]:
    print "FinalRank:" + str(l.pr) + "\t" + str(l.node_num)

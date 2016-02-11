#!/usr/bin/env python

import sys

from collections import namedtuple

Line = namedtuple('Line', 'node_num iter_num pr prev_pr connected_nodes')
NUM_ITERS = 1

def parse_line(line):
    l = line.strip().split("\t")
    assert len(l) == 2
    key = l[0]
    value = l[1]
    assert key.startswith("NodeId:")
    node_num = int(key[7:])
    value = value.split(",")
    iter_num = int(value[0][1:])
    pr = float(value[1])
    prev_pr = float(value[2])
    connected_nodes = map(int, value[3:]) if len(value) > 3 else []
    return Line(node_num, iter_num, pr, prev_pr, connected_nodes)

def stringify_Line(l):
    output = "NodeId:" + str(l.node_num) + "\t"
    output += "i" + str(l.iter_num) + "," + str(l.pr) + "," + str(l.prev_pr)
    if len(l.connected_nodes) > 0:
        output += "," + (','.join(map(str, l.connected_nodes)))
    output += "\n"
    return output

final_output = []
line = sys.stdin.readline()
if line.startswith("FinalRank"):
    final_output.append(line)
    for line in sys.stdin:
        final_output.append(line)
    for line in reversed(final_output):
        sys.stdout.write(line)
    sys.exit()
else:
    l = parse_line(line)
    final_output.append(l)

for line in sys.stdin:
    l = parse_line(line)
    final_output.append(l)

avg_diff = sum([abs(line.pr - line.prev_pr) for line in final_output]) / len(final_output)

if avg_diff < 0.00001 or final_output[0].iter_num == NUM_ITERS:
    # sort in descending order by pagerank
    final_output = sorted(final_output, key=lambda line: line.pr, reverse=True)

    for l in final_output[:20]:
        print "FinalRank:" + str(l.pr) + "\t" + str(l.node_num)
else:
    for l in final_output:
        sys.stdout.write(stringify_Line(l))

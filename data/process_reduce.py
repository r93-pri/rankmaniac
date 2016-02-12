#!/usr/bin/env python

import sys

from collections import namedtuple

Line = namedtuple('Line', 'node_num iter_num rank pr prev_pr connected_nodes')
NUM_ITERS = 50

def parse_line(line):
    l = line.strip().split("\t")
    assert len(l) == 2
    key = l[0]
    value = l[1]
    assert key.startswith("NodeId:")
    node_num = int(key[7:])
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


final_output = []
for line in sys.stdin:
    l = parse_line(line)
    final_output.append(l)

avg_diff = sum([abs(line.pr - line.prev_pr) for line in final_output]) / len(final_output)

if avg_diff < 0.00001 or final_output[0].iter_num == NUM_ITERS:
    # sort in descending order by pagerank
    final_output = sorted(final_output, key=lambda line: line.pr, reverse=True)

    for l in final_output[:20]:
        print "FinalRank:" + str(l.pr) + "\t" + str(l.node_num)
    sys.exit(1)
else:
    for l in final_output:
        sys.stdout.write(stringify_Line(l))

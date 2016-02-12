#!/usr/bin/env python

import sys
import numpy
import itertools

from collections import namedtuple

Line = namedtuple('Line', 'node_num iter_num rank pr prev_pr connected_nodes')
NUM_ITERS = 50
NUM_STABLE = 30

def top_k_indices_and_rest(ranks, k):
    partitioned_indices = numpy.argpartition(ranks, -k)
    unordered_top_k_indices = partitioned_indices[-k:]
    unordered_top_k_ranks = ranks[unordered_top_k_indices]
    ascending_top_k_indices = unordered_top_k_indices[numpy.argsort(unordered_top_k_ranks)]
    return (ascending_top_k_indices, partitioned_indices[:-k])

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

all_page_ranks = numpy.fromiter(itertools.imap(lambda l: l.pr, final_output), numpy.float, count=len(final_output))
(top_indices, rest_indices) = top_k_indices_and_rest(all_page_ranks, NUM_STABLE)

# Update all the ranks
changed = False
rank = NUM_STABLE - 1
for i in top_indices:
    if final_output[i].rank != rank:
        final_output[i] = final_output[i]._replace(rank=rank)
        changed = True
    rank -= 1

if not changed or final_output[0].iter_num == NUM_ITERS:
    for i in reversed(top_indices[-20:]):
        l = final_output[i]
        print "FinalRank:" + str(l.pr) + "\t" + str(l.node_num)

    # IMPORTANT: CHANGE THIS TO sys.exit(1) FOR LOCAL TESTING
    sys.exit()
else:
    # Clear ranks that were not updated
    for i in rest_indices:
        final_output[i] = final_output[i]._replace(rank=-1)

    for l in final_output:
        sys.stdout.write(stringify_Line(l))

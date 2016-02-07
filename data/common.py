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

def stringify_Line(l):
    output = "NodeId:" + str(l.node_num) + "\t"
    output += "i" + str(l.iter_num) + "," + str(l.pr) + "," + str(l.prev_pr)
    if len(l.connected_nodes) > 0:
        output += "," + (','.join(map(str, l.connected_nodes)))
    output += "\n"
    return output

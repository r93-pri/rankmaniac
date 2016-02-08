#!/usr/bin/env python

import sys
from common import *

#
# This program simply represents the identity function.
#
final_output = []
for line in sys.stdin:
    l = parse_line(line)
    if l.iter_num == 50:
        final_output.append(l)
    else:
        sys.stdout.write(line)

for l in final_output[:20]:
    print "FinalRank:" + str(l.pr) + "\t" + str(l.node_num)

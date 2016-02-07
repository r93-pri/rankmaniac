#!/usr/bin/env python

import sys
from common import *

#
# This program simply represents the identity function.
#

for line in sys.stdin:
    l = parse_line(line)
    if l.iter_num == 50:
        print "FinalRank:" + str(l.pr) + "\t" + str(l.node_num)
    else:
        sys.stdout.write(line)

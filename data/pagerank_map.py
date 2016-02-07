#!/usr/bin/env python

import sys
from common import *

#
# This program simply represents the identity function.
#

for line in sys.stdin:
    l = parse_line(line)
    l = l._replace(iter_num=(l.iter_num + 1))  # We increment the number of iterations each time
    sys.stdout.write(stringify_Line(l))

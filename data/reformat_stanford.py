# This is the code I wrote to reformat web-Stanford.txt to the format we use.
# It should work for any data set with two tab-separated columns,
# the first being the "from node" and the second being the "to node".

nodes = {}

with open('web-Stanford.txt', 'r') as f:
    for line in f:
        data = line.strip().split('\t')
        assert len(data) == 2
        fn = data[0]
        tn = data[1]
        if fn not in nodes:
            nodes[fn] = []
        nodes[fn].append(tn)

for k, v in nodes.iteritems():
	print "NodeId:" + k + '\t' + '1.0,0.0,' + ','.join(v)

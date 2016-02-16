# Implementation
## Data structures

Our program only makes use of one data structure, called Line. It represents the data passed on one line: the node number, the current iteration (1 through 50), the node’s rank (used for checking the stopping condition), its PageRank value, its previous PageRank value, and the list of nodes connected to it. It is implemented with a Python namedtuple, a tool for creating lightweight objects that support dot notation.
Data is passed between processes internally with a slightly modified version of the input file syntax. Specifically, we prefixed the value for each key with “i{iteration number},r{rank}”. The input file syntax is the same, and those fields are added on the first iteration.

## Parsing

Pagerank_map.py, pagerank_reduce.py, and process_reduce.py accept string input one line at a time, convert it to a useful data structure, perform operations on it, and then convert it back to a string to be passed to the next step. They each use two functions called parse_line(), which takes in a string and does the necessary conversion to a Line object, and stringify_Line(), which takes in a Line object and outputs a string that can be parsed by the next process.

## Local testing

In order to analyze performance in local testing, we needed a dataset much bigger than the provided sample data. We downloaded the [Stanford Web Graph](https://snap.stanford.edu/data/web-Stanford.html) dataset from 2003, which includes over two million edges and over a quarter million nodes, and adjusted it to match the format in which Rankmaniac expects to receive data using a short Python script.

We also needed a way to easily run multiple iterations of the entire process locally, so we created a local_test.py script which constructs a terminal command by concatenating an extra-iteration command string some number of times. Our first implementation simply piped the scripts together, which worked well until we started attempting to print FinalRank and exit early before the last iteration. Since pipes ignore regular process exit status codes, the pipe would just pass the FinalRank output on to the next process, which would not be able to parse the input. To fix this, we added a sys.exit(1) call after printing FinalRank and strung the commands together using && and file input/output so that the whole sequence stops as soon as one process “fails” (finishes).


    x **=** int(sys**.**argv[1])
    **assert** x **>** 0
    
    cmd **=** "(python pagerank_map.py < input.txt | sort > tmpA.txt && python pagerank_reduce.py < tmpA.txt > tmpB.txt && python process_map.py < tmpB.txt | sort > tmpA.txt && python process_reduce.py < tmpA.txt"
    cmd **+=** (x **-** 1) ***** " > tmpB.txt && python pagerank_map.py < tmpB.txt | sort > tmpA.txt && python pagerank_reduce.py < tmpA.txt > tmpB.txt && python process_map.py < tmpB.txt | sort > tmpA.txt && python process_reduce.py < tmpA.txt"
    cmd **+=** " && rm tmpA.txt tmpB.txt ) || (cat tmpB.txt && rm tmpA.txt tmpB.txt)"
    
    os**.**system(cmd)
## PageRank

PageRank calculates the importance of web pages based on how many pages link to some page. It is determined by first representing the network as a transition matrix αP + (1−α)/n * (1n×n) where P describes the probability of moving from one page to another. α is the dampening factor, which represents the probability that a person decides to continue clicking links. The PageRank of the sites in the network is found by calculating the stationary distribution of that transition matrix. Since a 1 is placed in the Pi,i position for site i if it does not have any outgoing links, pages with no outgoing links are favored with a higher PageRank. The stationary distribution can be solved directly by finding r such that r = rαP + (1−α)/n * (1n×n) and the values of r sum up to 1. This results in a systems of equations relating r and the transition matrix.
Attempting to solve a systems of equations of a large matrix that describes a network with many nodes to obtain the stationary distribution requires a lot of memory. Fortunately, the matrix is sparse (a single node will have outgoing links to few other links) so there is no need to hold the entire matrix in memory. Only the position and value of the nonzero values are needed. However, this method still requires solving a system of equations for every link, which is computationally expensive and not easily parallelizable. Thus, instead of solving for the stationary distribution of the transition matrix of all the outgoing links directly, we use an iterative approach by multiplying an arbitrary starting distribution by the transition matrix multiple times until the vector converges to the stationary distribution. Each element in the new candidate PageRank vector can be computed independently of the others as a dot product of the vector and the corresponding column in the transition matrix, allowing the task to be parallelizable and easily implemented with MapReduce. 

## MapReduce

MapReduce works well on tasks that can be broken down into smaller tasks whose results are merged. This lends itself perfectly to calculating PageRank iteratively. Each dot product is the sum of products between an incoming link's candidate PageRank and the probability that this link is clicked. The dampening factor is then applied to the sum. Map() can emit each smaller product as the graph's adjacency list is streamed by iterating over each node’s neighboring nodes. It emits the tuple (neighbor node, PageRank/(# of outgoing links)). It sets the key to be the neighboring node and the value to be the node’s own PageRank multiplied by the probability of clicking the neighbor node, since the value will be a part of the neighbor's dot product. Since the network's transition matrix is sparse, map() will only have to emit a relatively small number of values as it will only emit something for each nonzero element. It does not even have to perform any computation for the elements that are zero since they are skipped over when iterating over the neighboring nodes. These tuples are then sorted by key and collected. Values with the same key are summed in reduce() to get the dot product, and the dampening factor is applied to get the new candidate PageRank.
Despite having to perform this multiple times, with a good stopping condition and running in parallel this ends up being not as time-consuming as solving for the distribution directly.

# Optimization
## Python/code design optimization

Once we had a working PageRank implementation, we turned to optimizing it. Our first attempts focused on improving the performance of our Python code. The impact of these optimizations was fairly minimal, and most of them didn’t make it into our final code.

We used Python’s cProfile function, which can observe the running of any Python program and record profiling data, and the snakeviz package, which allows interactive visualization of the profiling data, to identify bottlenecks in our program.

![snakeviz](https://d2mxuefqeaa7sj.cloudfront.net/s_45E3279252CE7B756E384CBB516C3A904ECA0CAD474D79897DE770FFB96F0B2F_1455472311004_image_2016-02-14_09-50-39.png)


We found that the single thing slowing our code down the most was repeatedly converting the data from strings to integers, so we could work with them, and then back to strings so that they can be passed on to the next function. Our first implementation did this conversion with map(int, my_list) and map(str, my_list), which has excellent performance in Python. Doing this with a map is vastly more efficient than with a for loop in Python because function name lookups are fairly expensive in Python, and with a loop the int() or str() functions would have to be looked up on each loop, while with a map they only have to be looked up once. We tried to optimize this step further by using numpy’s built-in numpy.fromstring() function, which is designed precisely for converting a delimiter-separated string of numbers into a list of integers. This change sped up our parse_line function by approximately 20%. Overall, it didn’t make a significant impact on performance, so we reverted to using map() to eliminate the extra added dependency on a non-core library.

Other optimizations we attempted in light of the profiling data include switching from string.split to string.find (no significant change, the former function is already well optimized); switching from string.startswith to an explicit slice (slightly faster, but not worth the loss of safety); and removing assert checks in our code (again slightly faster, but not worth the downsides).

Finally, the biggest performance win we could have achieved by changing our implementation code would have come from switching from namedtuples to dictionaries for our data structure. Since namedtuples are immutable, the _replace() function actually constructs an entirely new namedtuple, which is very slow. We use the _replace() function very frequently, and switching to dictionaries or classes, which are mutable, would have vastly sped up that process. We decided to continue using namedtuples despite the performance cost because of the development advantages - namely, no chance of making typos that silently cause serious errors and ease of definition and use.

## Stopping conditions

The naive implementation of our PageRank algorithm performs 50 map-reduce iterations before halting and outputting the results. We retained this hard cap on the number of iterations, but provided additional stopping conditions so that we could minimize computation time while still maintaining correctness.

The first stopping condition implemented involved computing the average change in PageRank over the previous iteration, halting if this value was less than some epsilon. We arbitrarily chose epsilon to be 0.00001. This stopping condition vastly reduced our computation time as the PageRank values often stabilized well before the 50 iterations were complete. We discussed increasing the epsilon in an effort to trade correctness for speed, but it proved difficult to quantify the benefit of a given increase well enough to know that it was an overall gain.

Instead of increasing this epsilon, we implemented a more promising stopping condition that takes advantage of the fact that we’re only required to compute the ordering of 20 nodes with the greatest PageRank. We keep track of the top 30 nodes (as well as their order) after every iteration, and we halt if this order does not change between two subsequent iterations. We chose to wait for the ordering of the top 30 nodes to stabilize rather than just the top 20 because this better handles situations in which the PageRank of a rising node has a delayed impact on the final top 20 nodes.

This optimization takes advantage of the heavy-tail distribution of PageRank values. Since the top nodes contain most of the total PageRank from all of the edges, we should expect that they have very large but relatively different rankings. We can just look at the ranks of these top nodes, ignoring nodes of lower rank, since we can expect nodes with a larger PageRank value to increase quickly and separate from those of lower PageRank values. Further, within this collection of top nodes, we should similarly expect that their ordering will quickly become apparent (and not change much later on).

Our algorithm involved determining the nodes with the top 30 PageRanks after each iteration. The naive approach would be to sort the entire list of nodes by PageRank, thus revealing the top 30 ranks. We deemed such an approach unacceptable since sorting would require `O(n*log(n))` time on each and every iteration. We instead found an approach that only required linear time since the number of nodes might be very large, and we didn’t want to incur a large time penalty during our attempt to reduce the runtime of our algorithm. Using the numpy `argpartition` function on our list of node rankings, we were able to determine the top 30 nodes in linear time. Afterwards, we sorted this must smaller list in `O(30*log(30)) = O(1)` constant time with respect to the number of nodes. Note that the time complexity scales more than linearly with the number of nodes we attempt to stabilize, but 30 is a relatively small number and we simply care that it doesn’t scale with the size of the input.

This stopping condition optimization was sufficient for our algorithm to achieve a score greater than that of Milestone 1. For further optimization, we would have next looked into reducing the number of nodes we require to stabilize to 25 or less, as it might be possible to achieve an almost correct result with a lower threshold, improving our running time.

# Research

We will discuss some potential optimization strategies that we researched but did not implement due to either complexity of implementation or lack of time. Below is an overview of the most relevant and promising research we found on the topic.

## Fast and Exact Top-k Algorithm for PageRank 

https://www.aaai.org/ocs/index.php/AAAI/AAAI13/paper/viewFile/6162/6875

This paper describes an algorithm called F-Rank that can efficiently find the nodes with the top-k PageRank scores without sacrificing accuracy. Their algorithm iteratively estimates upper and lower PageRank bounds and then prunes unnecessary nodes and edges in each iteration. Specifically, the paper discusses a method to choose which nodes to prune such that the resulting nodes are actually those with the top PageRank. F-Rank first uses breadth-first search to construct the subgraphs of nodes relevant to computing the top-k PageRanks, and then computes the random walk probabilities for each node in the subgraphs. The F-Rank algorithm takes advantage of the heavy tail-distribution of the graph in order to quickly compute the PageRank. Since the top-k nodes will have much larger PageRanks than the lower ranked nodes, we’re able to trim them from the graph without sacrificing accuracy. This approach performs very well in practice according to the tests run by the researchers.

Expressing this algorithm as a map-reduce problem proved not to be straightforward. Each iteration involves computing the upper and lower bound, but each of these computations themselves require a breadth-first search. Though it is possible to do a breadth-first search using map-reduce, it’s uncertain how this ought to be structured in the case where a breadth-first search must be performed in every iteration of the algorithm. Specifically, map-reduce BFS requires multiple map and reduce calls with every iteration, but we cannot have multiple `BFS_map` and `BFS_reduce` calls per single `PR_map` and `PR_reduce` call. Further, traversing the graph as such would require a different program structure as the graph data of all nodes would have to be present during each map stage, and some preprocessing would be required to make the data representation ideal for BFS (since the graph data is currently stored as an adjacency list).

# Individual Contributions

Alex focused on parsing, data structures, Python optimizations, and the local testing scripts/data. Mimi implemented PageRank and ensured correct ordering of results. Jaden focused on researching optimization strategies and implementing the stopping condition optimization. 

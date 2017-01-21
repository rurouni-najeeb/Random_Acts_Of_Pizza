#################################################################################
##
## Class for the Shapley Value based Influence Graph
## Calculates the Shapley values of all nodes of the graph
##
## By: Zafarullah Mahmood
## Place: New Delhi
## Last Updated: 04/27/2016
##
## Copied By: Harsh Vijay
################################################################################

import numpy.random as nprnd
import operator
import copy

class Graph:
	"""
	Class for Shapley Value based Influence Graph
	Contains methods to calcualte the Shapley values of
	nodes as well as lambda coverage
	"""

	def __init__(self, adj_mat, directed = True):
		"""
		Initializes a graph object
		Return type: Graph object
		"""

		edges = 0
		adj_list = {i: [] for i in range(len(adj_mat))}
		for i in range(len(adj_mat)):
			for j in range(len(adj_mat)):
				if not adj_mat[i][j] == 0:
					adj_list[i].append(j)
					edges += 1

		self.adj_mat = copy.deepcopy(adj_mat)
		self.nodes = len(adj_mat)
		self.edges = edges
		self.is_directed = directed
		self.adj_list = adj_list
		self.active_nodes = [False for i in range(len(adj_mat))]
		self.theta = [nprnd.random() for i in range(len(adj_mat))]
		self.shapley_rank = dict()

	def thresh_f(self, i):
	    """
	    returns the value of threshold function for node i
	    it is the sum of weights of all active neighbours
	    of i
	    Return type:float
	    """
	    t = 0
	    for j in self.adj_list[i]:
	        if self.active_nodes[j] == True:
	            t += self.adj_mat[i][j]
	    return t

	def deactivate_all(self):
	    """
	    Deactivates all nodes
	    We have to do this for every iteration in
	    calcuation of Marginal Contribution
	    Return type: None
	    """
	    self.active_nodes = [False for i in range(self.nodes)]

	def v(self, i):
	    """
	    Returns the contribution of node i
	    It is equal to the number of nodes that get activated
	    due to the activation of node i. If a node is already
	    activated, its contribution is zero
	    Return type: Int
	    """

	    # Check whether the node is already active
	    if self.active_nodes[i] == True:
	        return 0

	    self.active_nodes[i] = True
	    contrib = 0

	    for j in self.adj_list[i]:
	        if self.thresh_f(j) >= self.theta[j] and self.active_nodes[j] == False:
	            self.active_nodes[j] = True
	            contrib += 1 + self.v(j)

	    return contrib

	def shapley(self, R, t):
	    """
	    Returns Shapley values of all nodes by taking
	    a randomly generated sample of permuations of
	    nodes.
	    Return type: Dict
	    """
	    n = self.nodes

	    # phi contains the shapley values of nodes
	    phi = [0 for i in range(n)]

	    # MC, i.e., marginal contribution of each node
	    # which reflects the change in coverage due to
	    # the addition of node i in the set of initilly
	    # activated nodes
	    MC = [0 for i in range(n)]

	    # randomly select t permutations from n! possible
	    # permutations of nodes
	    for j in range(t):
	        temp = [0 for i in range(n)]

	        # repeat the experiment R times (take the average)
	        for r in range(R):
	            self.theta = nprnd.random_sample((n,))
	            self.deactivate_all()
	            k = nprnd.permutation(n)
	            for i in k:
	                temp[i] += self.v(i)

	        # Add the contribution for each permuation
	        for i in range(n):
	            MC[i] += temp[i]*1.00/R

	    for i in range(n):
	        phi[i] = (MC[i]*1.00)/t

	    x = {i: phi[i] for i in range(n)}
	    self.shapley_rank = sorted(x.items(), key=operator.itemgetter(1), reverse=True)

	    return self.shapley_rank


	def is_adj(self, i, topknodes):
		"""
		Checks whether is a neighbour of any of the nodes
		in the list topknodes
		Return type: Bool
		"""
		for node in topknodes:
			if i in self.adj_list[node]:
				return True
		return False

	def top_k(self, k = 1):
	    """
	    Given the value of k, returns the top K
	    influential nodes in the graph. Makes sure
	    the nodes are as far apart as possible.
	    i.e., tries to avoid considering a node
	    which has a neighbour as an influential
	    node
	    Return type: List
	    """
	    if self.shapley_rank == {}:
	    	return []

	    n = self.nodes
	    topknodes = []
	    i = 0
	    count = 0
	    while count < k and not i == n:
	        if self.shapley_rank[i][0] not in topknodes and not self.is_adj(self.shapley_rank[i][0], topknodes):
	            topknodes.append(self.shapley_rank[i][0])
	            count += 1
	        i += 1
	    i = 0
	    if not count == k:
	        while not count == k:
	            if self.shapley_rank[i][0] not in topknodes:
	                topknodes.append(self.shapley_rank[i][0])
	                count += 1
	            i += 1
	    return topknodes

	def top_k_coverage(self, k, z = 100):
		n = self.nodes
		initially_active = self.top_k(k)
		total_contrib = 0
		for i in range(z):
			self.deactivate_all()
			self.theta = [nprnd.random() for i in range(n)]
			contrib = k
			for node in initially_active:
				contrib += self.v(node)
			if contrib <= n:
				total_contrib += contrib
			else:
				total_contrib += n
		return total_contrib/z


	def lmbd(self, lamb):
	    """
	    Returns a list of nodes that when initially activated at a particular theta
	    setting give a minimum coverage of lambda*100 %
	    Works as a helper function for lambda_coverage()
	    """
	    n = self.nodes

	   	# The top_k_nodes is a list of all nodes in descending
	    # order of influence
	    top_k_nodes = self.top_k(self.nodes)
	    for i in range(n):
			self.deactivate_all()
			initially_active = top_k_nodes[:i]

			total_contrib = i + 1
			for node in initially_active:
				total_contrib += self.v(node)

			coverage = total_contrib*1.00/n
			if coverage >= lamb:
				return top_k_nodes[:i]


	def lambda_coverage(self, lamb, z = 100):
		"""
		Returns a list of minimum nodes that are needed to cover the graph by a
	    factor lambda, i.e., at the end of activation at least lambda*100%
	    nodes are activated. Uses a helper function lmbd()
	    Return type: List
		"""
		n = self.nodes
		top_k_nodes = self.top_k(self.nodes)
		all_nodes = [n-1 for i in range(z)]
		for i in range(z):
			self.theta = [nprnd.random() for k in range(n)]
			all_nodes[i] = len(self.lmbd(lamb))
		avg_k = sum(all_nodes)/z
		return top_k_nodes[:avg_k]

from collections import defaultdict
adj_list = dict()
ls = set()
with open('graph.txt' , 'r') as f:
	cnt = 0
	while cnt < 4040:
	    try:
			har = f.readline().split(":")
			if not len(har):break
			key_ = har[0].rstrip()
			ls.add(key_)
			child_ = []
			if len(har) > 1:
				child_ = har[1].rstrip('\n').split()
			if key_ not in adj_list:adj_list[key_] = list()
			#if len(child_):print child_
			ls |= set(child_)
			for ix in child_:
			    adj_list[key_].append(ix)
			cnt += 1
	    except Exception as e:print str(e);break

give_no = dict()
give_name = dict()
cnt = 0
for i in ls:
	give_no[i] = cnt
	give_name[cnt] = i
	cnt += 1
adj_mat = [[0.0 for i in xrange(cnt)] for j in xrange(cnt)]
for i in ls:
	if i in adj_list:
		dic_ = adj_list[i]
		for j in ls:
			if j in dic_:
				adj_mat[give_no[i]][give_no[j]] = 1.0
#print adj_mat
#print give_no
#print len(ls)
g = Graph(adj_mat)

print 'Please wait... Calculating the Shapley value based ranks'
shapley_rank = g.shapley(100, 100)

fw = open('shapleyvalue.txt' , 'w+')
for key, value in shapley_rank:
	print "node = %3d\t node_name = %s\t Shapley value = %f"%(key,give_name[key], value)
	fw.write(str(give_name[key]) + " " + str(value) + '\n')
fw.close()

print '\nTop 5 nodes:'
print g.top_k(50)

print  '\nNodes for 60% coverage:'
print g.lambda_coverage(0.6)

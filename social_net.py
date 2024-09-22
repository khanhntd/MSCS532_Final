import pickle
import operator
import networkx as nx
import matplotlib.pyplot as plt
from arcplot import *
from collections import defaultdict
from itertools import combinations
from dataset import downloadDataset

class SocialNetwork:
  def __init__(self, githubGraph: nx.Graph) -> None:
    self.githubGraph = githubGraph

  def drawGraph(self, degreeDistribution: bool = False) -> None:
    plt.figure(figsize=(8, 8))
    if degreeDistribution:
      plt.title(label="Github degree centrality")
      plt.hist(list(nx.degree_centrality(self.githubGraph).values()))
    else:
      plt.title(label="Github Network")
      nx.draw(self.githubGraph, with_labels=True)
    plt.show(block = False)
    plt.pause(5)

  # findImportantCollaborators will use degree centrality to determine the most important Github Developers
  # that works on the same project within a repo together
  def findImportantCollaborators(self) -> list[tuple]:
    degCent = nx.degree_centrality(self.githubGraph)
    degCent = {k: v for k, v in sorted(degCent.items(), key=lambda item: item[1], reverse=True)}
    maxDegCent = max(list(degCent.values()))
    importantCollaborators = [(n, dc) for n, dc in degCent.items() if dc == maxDegCent]
    return importantCollaborators

  # connectCommunities will find the two largest communities based on the cliques and
  # determine the bottleneck user based on their collaborations or followers
  # Afterwards, if there is a path or similar interest between them, we can
  # recommend the repository for the followers that those bottleneck users work at
  # to increase the reach
  def connectCommunities(self):
    cliques = sorted(nx.find_cliques(self.githubGraph), key=lambda x: len(x))
    largestClique = self.githubGraph.subgraph(set(cliques[-1])).copy()
    secondLargestClique = self.githubGraph.subgraph(set(cliques[-2])).copy()
    largestCliqueBetweenessCentrality = nx.betweenness_centrality(largestClique)
    secondLargestCliqueBetweenessCentrality = nx.betweenness_centrality(secondLargestClique)
    largestCliqueBottleneckUser = max(largestCliqueBetweenessCentrality, key=largestCliqueBetweenessCentrality.get)
    secondLargestCliqueBottleneckUser = max(secondLargestCliqueBetweenessCentrality, key=secondLargestCliqueBetweenessCentrality.get)
    if self.pathExistBFS(largestCliqueBottleneckUser, secondLargestCliqueBottleneckUser):
      print("Connect two largest clique together between {0} and {1}".format(largestCliqueBottleneckUser, secondLargestCliqueBottleneckUser))

  # findLargestCommunities can find the largest cliques
  # based on the shared interest
  # (e.g Github Sponsor https://github.com/sponsors/explore)
  def findLargestCommunities(self):
    largestClique = set(sorted(nx.find_cliques(self.githubGraph), key=lambda x: len(x))[-1])
    githubLargestClique = self.githubGraph.subgraph(largestClique).copy()
    # Go out 1 degree of separation
    for node in list(githubLargestClique.nodes()):
        githubLargestClique.add_nodes_from(self.githubGraph.neighbors(node))
        githubLargestClique.add_edges_from(zip([node]*len(list(self.githubGraph.neighbors(node))), self.githubGraph.neighbors(node)))

    nodePosition = nx.spring_layout(githubLargestClique)
    plt.figure(figsize=(8, 8))
    plt.title("Largest Clique in the Graph")
    nx.draw(githubLargestClique, nodePosition, with_labels=True)
    plt.show(block = False)
    plt.pause(5)

  # recommendedCollaborators will recommend the github users who collaborated to other collaborators in the past and
  # but hasn't had any collaborations with their neighbors's collaborators
  # by using BFS to determine if there is a shortest path between them
  def recommendedCollaborators(self) -> list[tuple]:
    recommendedCollaborators = defaultdict(int)
    for node, _ in self.githubGraph.nodes(data=True):
        # Create a combination of 2 with all the neighbor nodes that the node has
        # and determine if there is a path between them. If not,
        # add them
        for firstNeighborCollab, secondNeighborCollab  in combinations(self.githubGraph.neighbors(node), 2):
            if not self.pathExistBFS(firstNeighborCollab, secondNeighborCollab):
                recommendedCollaborators[(firstNeighborCollab, secondNeighborCollab)] += 1

    # Identify the top 10 pairs of users
    sortedRecommendedCollaborators = sorted(recommendedCollaborators.values())
    top10Pairs = [pair for pair, count in recommendedCollaborators.items() if count > sortedRecommendedCollaborators[-10]]
    return top10Pairs

  # pathExistBFS will use breath first search
  # https://www.geeksforgeeks.org/breadth-first-search-or-bfs-for-a-graph/#
  # to determine if the path between two vertexes are connected in the shortest way possible
  # Step 1: Begins with a node, traverses all its adjacent
  # Step 2: Once all adjacent are visited, then their adjacent are traversed
  # Time Complexity: O(v + e) (since its traverse through all vertex and edge in worst case)
  def pathExistBFS(self, startVertex: int, endVertex: int) -> bool:
    visitedNodes = set()
    # Begin traverse from the starting node
    queue = [startVertex]

    # Traverse all its adjacent node
    for node in queue:
        # Once all adjacent are visited, then their adjacent are traversed
        neighbors = self.githubGraph.neighbors(node)
        if endVertex in neighbors:
            return True
        else:
            visitedNodes.add(node)
            queue.extend([n for n in neighbors if n not in visitedNodes])

        # Check to see if there are any vertex that can be reached from the current node adjacent
        # in order to know if there are any path that BFS can traverse
        if node == queue[-1]:
            return False


def createSocialNet() -> SocialNetwork:
  dataPath = downloadDataset()
  with open(dataPath[1], 'rb') as f:
    githubGraph = pickle.load(f)

  # Since pilotlib has a problem with performance for over than 2000 nodes with the corresponding edges
  # We will only take the 150 nodes which have the highest degree (nodes that have most edges)
  # and simulate a subgraph of github
  githubNodeDegree = dict(githubGraph.degree())
  sortedNodes = sorted(githubNodeDegree.items(), key=lambda x: x[1], reverse=True)
  topDegreeNodes = [node for node, _ in sortedNodes[:200]]
  githubSubGraph = githubGraph.subgraph(topDegreeNodes)
  print("Number of nodes", len(githubSubGraph.nodes()))
  print("Number of edges", len(githubSubGraph.edges()))
  print("Number of nodes", githubSubGraph.nodes())
  sn = SocialNetwork(githubSubGraph)
  # sn.drawGraph()
  return sn


def socialNetworkAnalysis() -> None:
  sn = createSocialNet()
  importantColaborators = sn.findImportantCollaborators()
  print("The most prolific colaborators", importantColaborators)
  #sn.drawGraph(degreeDistribution=True)
  #sn.findLargestCommunities()
  sn.connectCommunities()
  recommendedCollaborators = sn.recommendedCollaborators()
  print("Top 10 recommended collaborators:", recommendedCollaborators)

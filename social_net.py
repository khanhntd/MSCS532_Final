import pickle
import networkx as nx
import matplotlib.pyplot as plt
from arcplot import *
from collections import defaultdict
from itertools import combinations
from dataset import downloadDataset

class SocialNetwork:
  def __init__(self, fbGraph: nx.Graph) -> None:
    self.fbGraph = fbGraph

  def drawGraph(self, degreeDistribution: bool = False) -> None:
    plt.figure(figsize=(8, 8))
    if degreeDistribution:
      plt.title(label="Facebook degree centrality")
      plt.hist(list(nx.degree_centrality(self.fbGraph).values()))
    else:
      plt.title(label="Facebook Network")
      nx.draw(self.fbGraph, with_labels=True)
    plt.show(block = False)
    plt.pause(5)

  # findImportantPeople will use degree centrality to determine the most important Facebook person
  # that have many friends or being followed by others facebook user
  def findImportantPeople(self) -> list[tuple]:
    degCent = nx.degree_centrality(self.fbGraph)
    degCent = {k: v for k, v in sorted(degCent.items(), key=lambda item: item[1], reverse=True)}
    maxDegCent = max(list(degCent.values()))
    importantPeople = [(n, dc) for n, dc in degCent.items() if dc == maxDegCent]
    return importantPeople

  # connectCommunities will find the two largest communities based on the cliques and
  # determine the bottleneck user based on the number of friends or followers
  # they have. Afterwards, if there is a path or similar interest between them, we can
  # recommend the bottle neck's user to other followers/friends
  # to increase the reach
  def connectCommunities(self)-> None:
    cliques = sorted(nx.find_cliques(self.fbGraph), key=lambda x: len(x))
    largestClique = self.fbGraph.subgraph(set(cliques[-1])).copy()
    secondLargestClique = self.fbGraph.subgraph(set(cliques[-2])).copy()
    largestCliqueBetweenessCentrality = nx.betweenness_centrality(largestClique)
    secondLargestCliqueBetweenessCentrality = nx.betweenness_centrality(secondLargestClique)
    largestCliqueBottleneckUser = max(largestCliqueBetweenessCentrality, key=largestCliqueBetweenessCentrality.get)
    secondLargestCliqueBottleneckUser = max(secondLargestCliqueBetweenessCentrality, key=secondLargestCliqueBetweenessCentrality.get)
    print("Is path exist between two bottleneck users:", self.pathExistBFS(largestCliqueBottleneckUser, secondLargestCliqueBottleneckUser))
    if self.pathExistBFS(largestCliqueBottleneckUser, secondLargestCliqueBottleneckUser):
      print("Connect two largest clique together between {0} and {1}".format(largestCliqueBottleneckUser, secondLargestCliqueBottleneckUser))

  # findLargestCommunities can find the largest cliques
  # based on the shared interest
  # (e.g https://www.wired.com/story/facebook-people-you-may-know-friend-suggestions/ )
  def findLargestCommunities(self)-> None:
    largestClique = set(sorted(nx.find_cliques(self.fbGraph), key=lambda x: len(x))[-1])
    facebookLargestClique = self.fbGraph.subgraph(largestClique).copy()
    print("Facebook largest clique", facebookLargestClique.nodes())
    # Go out 1 degree of separation
    for node in list(facebookLargestClique.nodes()):
        facebookLargestClique.add_nodes_from(self.fbGraph.neighbors(node))
        facebookLargestClique.add_edges_from(zip([node]*len(list(self.fbGraph.neighbors(node))), self.fbGraph.neighbors(node)))

    nodePosition = nx.spring_layout(facebookLargestClique)
    plt.figure(figsize=(8, 8))
    plt.title("Largest Clique in the Facebook Graph")
    nx.draw(facebookLargestClique, nodePosition, with_labels=True)
    plt.show(block = False)
    plt.pause(5)

  # recommendedFriends will recommend friends who shared similar interest
  # but hasn't been friends yet by creating a combination between the current user's neighbor
  # If there is no connection, we will recommend them
  def recommendedFriends(self) -> list[tuple]:
    recommendedFriends = defaultdict(int)
    for node, _ in self.fbGraph.nodes(data=True):
        # Create a combination of 2 with all the neighbor nodes that the node has
        # and determine if there is a path between them. If not,
        # add them
        for firstNeighborFriend, secondNeighborFriend  in combinations(self.fbGraph.neighbors(node), 2):
            if not self.pathExistBFS(firstNeighborFriend, secondNeighborFriend):
                recommendedFriends[(firstNeighborFriend, secondNeighborFriend)] += 1

    # Identify the top 10 pairs of users
    sortedRecommendedFriends = sorted(recommendedFriends.values())
    top10Pairs = [pair for pair, count in recommendedFriends.items() if count > sortedRecommendedFriends[-10]]
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
        neighbors = self.fbGraph.neighbors(node)
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
    fbGraph = pickle.load(f)

  # Since pilotlib has a problem with performance for over than 2000 nodes with the corresponding edges
  # We will only take the 200 nodes which have the highest degree (nodes that have most edges)
  # and simulate a subgraph of fb
  fbNodeDegree = dict(fbGraph.degree())
  sortedNodes = sorted(fbNodeDegree.items(), key=lambda x: x[1], reverse=True)
  topDegreeNodes = [node for node, _ in sortedNodes[:200]]
  fbSubGraph = fbGraph.subgraph(topDegreeNodes)
  print("Number of nodes", len(fbSubGraph.nodes()))
  print("Number of edges", len(fbSubGraph.edges()))
  print("Number of nodes", fbSubGraph.nodes())
  sn = SocialNetwork(fbSubGraph)
  #sn.drawGraph()
  return sn


def socialNetworkAnalysis() -> None:
  sn = createSocialNet()
  importantPeople = sn.findImportantPeople()
  print("The most prolific people", importantPeople)
  #sn.drawGraph(degreeDistribution=True)
  #sn.findLargestCommunities()
  sn.connectCommunities()
  recommendedFriends = sn.recommendedFriends()
  print("Top 10 recommended friends:", recommendedFriends)

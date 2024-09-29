import pickle
import networkx as nx
import matplotlib.pyplot as plt
from arcplot import *
from collections import defaultdict
from itertools import combinations
from dataset import downloadDataset
import heapq

class SocialNetwork:
  def __init__(self, fbGraph: nx.Graph) -> None:
    self.fbGraph = fbGraph
    # To record all the traverse path for all the nodes
    # to determine if the current node has traverse all path before
    self.traversePath = self.traversePathWithAllNodes()

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
  def connectCommunities(self)-> int:
    cliques = sorted(nx.find_cliques(self.fbGraph), key=lambda x: len(x))
    largestClique = self.fbGraph.subgraph(set(cliques[-1])).copy()
    secondLargestClique = self.fbGraph.subgraph(set(cliques[-2])).copy()
    largestCliqueBetweenessCentrality = nx.betweenness_centrality(largestClique)
    secondLargestCliqueBetweenessCentrality = nx.betweenness_centrality(secondLargestClique)
    largestCliqueBottleneckUser = max(largestCliqueBetweenessCentrality, key=largestCliqueBetweenessCentrality.get)
    secondLargestCliqueBottleneckUser = max(secondLargestCliqueBetweenessCentrality, key=secondLargestCliqueBetweenessCentrality.get)
    pathExist = self.pathExistBFS(largestCliqueBottleneckUser, secondLargestCliqueBottleneckUser)
    #distanceBetweenTwoUsers = self.getDistanceWithCurrentNode(largestCliqueBottleneckUser, secondLargestCliqueBottleneckUser)
    #print("Distance between two bottleneck users:", distanceBetweenTwoUsers)
    #print("There is path between the two largest clique", pathExist)
    if pathExist:
      print("Connect two largest clique together between {0} and {1}".format(largestCliqueBottleneckUser, secondLargestCliqueBottleneckUser))
    return 1

  # findLargestCommunities can find the largest cliques
  # based on the shared interest
  # (e.g https://www.wired.com/story/facebook-people-you-may-know-friend-suggestions/ )
  def findLargestCommunities(self, isDrawing: bool = False)-> nx.Graph:
    largestClique = set(sorted(nx.find_cliques(self.fbGraph), key=lambda x: len(x))[-1])
    facebookLargestClique = self.fbGraph.subgraph(largestClique).copy()
    print("Facebook largest clique", facebookLargestClique.nodes())
    # Go out 1 degree of separation
    for node in list(facebookLargestClique.nodes()):
        facebookLargestClique.add_nodes_from(self.fbGraph.neighbors(node))
        facebookLargestClique.add_edges_from(zip([node]*len(list(self.fbGraph.neighbors(node))), self.fbGraph.neighbors(node)))

    if isDrawing:
      nodePosition = nx.spring_layout(facebookLargestClique)
      plt.figure(figsize=(8, 8))
      plt.title("Largest Clique in the Facebook Graph")
      nx.draw(facebookLargestClique, nodePosition, with_labels=True)
      plt.show(block = False)
      plt.pause(5)

    return facebookLargestClique

  def traversePathWithAllNodes(self) -> set:
      traversePath = set()
      for node, _ in self.fbGraph.nodes(data=True):
        for neighbour in self.fbGraph.neighbors(node):
            if (node, neighbour) not in traversePath and self.pathExistBFS(node, neighbour):
                traversePath.add((node, neighbour))

      return traversePath

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
            #if (firstNeighborFriend, secondNeighborFriend) not in self.traversePath:
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

  def pathExistDFS(self, startVertex: int, endVertex: int) -> bool:
      visitedNodes = set()
      return self.findPathBetweenTwoNodesDFS(startVertex, endVertex, visitedNodes)

  # findPathBetweenTwoNodesDFS will use depth first search
  # https://www.geeksforgeeks.org/python-program-for-depth-first-search-or-dfs-for-a-graph/
  # Step 1: Begins with a node, traverses to the first neighbour of the current node
  # Step 2: Once the current neighboard node read the depth of it, then their adjacent are traversed
  # Time Complexity: O(v + e) (since its traverse through all vertex and edge in worst case)
  def findPathBetweenTwoNodesDFS(self, currentVertex: int, endVertex: int, visitedNodes: set) -> bool:
    if currentVertex == endVertex:
      return True

    visitedNodes.add(currentVertex)
    for neighbour in self.fbGraph.neighbors(currentVertex):
      if neighbour not in visitedNodes and self.findPathBetweenTwoNodesDFS(neighbour, endVertex, visitedNodes):
        return True

    return False

  # getDistanceWithCurrentNode will use dijkstra's algortihm
  # to get the shortest distance between two nodes
  # Time complexity: O((V + E) log V)
  # Space complexity: O(v)
  def getDistanceWithCurrentNode(self, startVertex: int, endVertex: int) -> int:
    queue = [(0, startVertex)]
    distances = {node: float('inf') for node in self.fbGraph.nodes()}
    distances[startVertex] = 0
    visitedNodes = set()

    while queue:
      currentDistance, currentNode = heapq.heappop(queue)
      if currentNode in visitedNodes:
        continue

      if endVertex == currentNode:
        return currentDistance

      for neighbor in self.fbGraph.neighbors(currentNode):
        if neighbor not in visitedNodes:
          newDistance = currentDistance + 1
          if newDistance < distances[neighbor]:
            distances[neighbor] = newDistance
            heapq.heappush(queue, (newDistance, neighbor))

    return -1

@profile
def createSocialNet() -> SocialNetwork:
  dataPath = downloadDataset()
  with open(dataPath[1], 'rb') as f:
    fbGraph = pickle.load(f)

  # Since pilotlib has a problem with performance for over than 2000 nodes with the corresponding edges
  # We will only take the 200 nodes which have the highest degree (nodes that have most edges)
  # and simulate a subgraph of fb
  fbNodeDegree = dict(fbGraph.degree())
  sortedNodes = sorted(fbNodeDegree.items(), key=lambda x: x[1], reverse=True)
  #topDegreeNodes = [node for node, _ in sortedNodes[:10000]]
  topDegreeNodes = [node for node in list(fbGraph.nodes())[:10000]]
  fbSubGraph = fbGraph.subgraph(topDegreeNodes)
  print("Number of nodes", len(fbSubGraph.nodes()))
  print("Number of edges", len(fbSubGraph.edges()))
  print("Number of nodes", fbSubGraph.nodes())
  sn = SocialNetwork(fbSubGraph)
  #sn.drawGraph()
  return sn



def socialNetworkAnalysis() -> None:
  sn = createSocialNet()
  #importantPeople = sn.findImportantPeople()
  #print("The most prolific people", importantPeople)
  #sn.drawGraph(degreeDistribution=True)
  #sn.findLargestCommunities()
  #sn.connectCommunities()
  recommendedFriends = sn.recommendedFriends()
  print("Top 10 recommended friends:", recommendedFriends)

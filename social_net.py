import pickle
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

  def findImportantCollaborators(self) -> list[str]:
    degCent = nx.degree_centrality(self.githubGraph)
    degCent = {k: v for k, v in sorted(degCent.items(), key=lambda item: item[1], reverse=True)}
    maxDegCent = max(list(degCent.values()))
    importantCelebrities = [n for n, dc in degCent.items() if dc == maxDegCent]
    return importantCelebrities

  def findCommunities(self):
    largestMaxClique = set(sorted(nx.find_cliques(self.githubGraph), key=lambda x: len(x))[-1])

    # Create a subgraph from the largest_max_clique: G_lm

    githubLargestMaxClique = self.githubGraph.subgraph(largestMaxClique).copy()

    # Go out 1 degree of separation
    for node in list(githubLargestMaxClique.nodes()):
        githubLargestMaxClique.add_nodes_from(self.githubGraph.neighbors(node))
        githubLargestMaxClique.add_edges_from(zip([node]*len(list(self.githubGraph.neighbors(node))), self.githubGraph.neighbors(node)))

    nodePosition = nx.spring_layout(githubLargestMaxClique)
    plt.figure(figsize=(8, 8))
    plt.title("Largest Clique in the Graph")
    nx.draw(githubLargestMaxClique, nodePosition, with_labels=True)
    plt.show(block = False)
    plt.pause(5)

  def recommendedCollaborators(self) -> list[tuple]:
    recommendedCollaborators = defaultdict(int)
    for node, _ in self.githubGraph.nodes(data=True):
        for firstNeighborCollab, secondNeighborCollab  in combinations(self.githubGraph.neighbors(node), 2):
            if not self.githubGraph.has_edge(firstNeighborCollab, secondNeighborCollab):
                recommendedCollaborators[(firstNeighborCollab, secondNeighborCollab)] += 1

    # Identify the top 10 pairs of users
    sortedRecommendedCollaborators = sorted(recommendedCollaborators.values())
    top10Pairs = [pair for pair, count in recommendedCollaborators.items() if count > sortedRecommendedCollaborators[-10]]
    return top10Pairs


def createSocialNet() -> SocialNetwork:
  dataPath = downloadDataset()
  with open(dataPath[1], 'rb') as f:
    githubGraph = pickle.load(f)

  # Since pilotlib has a problem with performance for over than 2000 nodes with the corresponding edges
  # We will only take the 250 nodes which have the highest degree (nodes that have most edges)
  # and simulate a subgraph of github
  githubNodeDegree = dict(githubGraph.degree())
  sortedNodes = sorted(githubNodeDegree.items(), key=lambda x: x[1], reverse=True)
  topDegreeNodes = [node for node, _ in sortedNodes[:25]]
  githubSubGraph = githubGraph.subgraph(topDegreeNodes)
  print("Number of nodes", len(githubSubGraph.nodes()))
  print("Number of edges", len(githubSubGraph.edges()))
  print("Edges:", githubSubGraph.edges())

  sn = SocialNetwork(githubSubGraph)
  sn.drawGraph()
  return sn

def socialNetworkAnalysis() -> None:
  sn = createSocialNet()
  importantColaborators = sn.findImportantCollaborators()
  print("The most prolific colaborators", importantColaborators)
  sn.drawGraph(degreeDistribution=True)
  sn.findCommunities()
  recommendedCollaborators = sn.recommendedCollaborators()
  print("Top 10 recommended collaborators:", recommendedCollaborators)

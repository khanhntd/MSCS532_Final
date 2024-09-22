import pickle
import networkx as nx
import matplotlib.pyplot as plt
from dataset import downloadDataset

class SocialNetwork:
  def __init__(self, twitterDiGraph: nx.DiGraph) -> None:
    self.twitterDiGraph = twitterDiGraph

  def drawGraph(self) -> None:
    plt.figure(figsize=(8, 8))
    nx.draw(self.twitterDiGraph, with_labels=True)
    plt.show()

def createSocialNet() -> SocialNetwork:
  dataPath = downloadDataset()
  with open(dataPath[0], 'rb') as f:
    twitterGraph = pickle.load(f)

  # Since Twitter is by default, has a natural model of end-users following their favorite celebrity
  # Therefore, we would need to convert the nodes, edges loading from dataset
  # and create a digraph
  twitterDiGraph = nx.DiGraph()
  edgesFromTGraph = [x for x in twitterGraph.edges(data=True) if x[0] in [1, 16, 18, 19, 28, 36, 37, 39, 42, 43, 45] if x[1] < 50]
  twitterDiGraph.add_edges_from(edgesFromTGraph)
  sn = SocialNetwork(twitterDiGraph)
  sn.drawGraph()
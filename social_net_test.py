import unittest
import pickle
import networkx as nx
from itertools import combinations
from collections import defaultdict
from social_net import SocialNetwork
from dataset import downloadDataset
from concurrent.futures import ThreadPoolExecutor

def runTest(test):
    """Run a single test case."""
    result = unittest.TestResult()
    test.run(result)
    return result

class TestSocialNetworkAnalysis(unittest.TestCase):


  # def StressTestingFrom1000To20000NodesForRecommendedFriendsWithUnsortedData(self):
  #   for numberOfNodes in range(1000, 20000, 1000):
  #     nodes = [node for node, _ in self.fbGraph.nodes[:numberOfNodes]]
  #     fbSubGraph = self.fbGraph.subgraph(nodes)
  #     sn = SocialNetwork(fbSubGraph)
  #     sn.recommendedFriends()
  # def StressTestingFrom1000To20000NodesForRecommendedFriendsWithSortedDegreeData(self):
  #   for numberOfNodes in range(0, 20000, 1000):
  #     nodes = [node for node, _ in self.fbGraph.nodes[:numberOfNodes]]
  #     fbSubGraph = self.fbGraph.subgraph(nodes)
  #     sn = SocialNetwork(fbSubGraph)
  #     sn.recommendedFriends()
  def test_FindRecommendedFriends(self):
    dataset = downloadDataset()
    with open(dataset[1], 'rb') as f:
      fbGraph = pickle.load(f)
    nodes = [node for node in list(fbGraph.nodes())[:1000]]
    fbSubGraph = fbGraph.subgraph(nodes)
    sn = SocialNetwork(fbSubGraph)
    recommendedFriends = sn.recommendedFriends()
    expectedRecommendedFriends = set()

    expectedRecommendedFriends = defaultdict(int)
    for node, _ in fbSubGraph.nodes(data=True):
        for firstNeighborFriend, secondNeighborFriend  in combinations(fbSubGraph.neighbors(node), 2):
            if not fbSubGraph.has_edge(firstNeighborFriend, secondNeighborFriend):
                expectedRecommendedFriends[(firstNeighborFriend, secondNeighborFriend)] += 1

    sortedExpectedRecommendedFriends = sorted(expectedRecommendedFriends.values())
    expectedRecommendedFriends = [pair for pair, count in expectedRecommendedFriends.items() if count > sortedExpectedRecommendedFriends[-10]]
    # Since it is unsorted node, there will be more guarantee to have friends instead
    self.assertGreater(len(recommendedFriends), 0)
    self.assertEqual(expectedRecommendedFriends, recommendedFriends)

  def test_FindImportantPeople(self):
    dataset = downloadDataset()
    with open(dataset[1], 'rb') as f:
      fbGraph = pickle.load(f)
    nodes = [node for node in list(fbGraph.nodes())[:1000]]
    fbSubGraph = fbGraph.subgraph(nodes)
    sn = SocialNetwork(fbSubGraph)
    importantPeople = sn.findImportantPeople()

    degCent = nx.degree_centrality(fbSubGraph)
    degCent = {k: v for k, v in sorted(degCent.items(), key=lambda item: item[1], reverse=True)}
    maxDegCent = max(list(degCent.values()))
    expectedImportantPeople = [(n, dc) for n, dc in degCent.items() if dc == maxDegCent]
    self.assertEqual(expectedImportantPeople, importantPeople)

  def test_TraversePathWillAllNodes(self):
    dataset = downloadDataset()
    with open(dataset[1], 'rb') as f:
      fbGraph = pickle.load(f)
    nodes = [node for node in list(fbGraph.nodes())[:1000]]
    fbSubGraph = fbGraph.subgraph(nodes)
    sn = SocialNetwork(fbSubGraph)
    for node, _ in fbSubGraph.nodes(data=True):
      for neighbour  in fbSubGraph.neighbors(node):
        if fbSubGraph.has_edge(node, neighbour):
          self.assertTrue((node, neighbour) in sn.traversePath)
    self.assertGreater(len(sn.traversePath), 0)

if __name__ == '__main__':
    unittest.main()
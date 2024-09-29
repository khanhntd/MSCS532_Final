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
  def test_StressTestingFrom1000To20000NodesForRecommendedFriendsWithUnsortedData(self):
      dataset = downloadDataset()
      with open(dataset[1], 'rb') as f:
        fbGraph = pickle.load(f)
      for numberOfNodes in range(1000, 20000, 1000):
        nodes = [node for node in list(fbGraph.nodes())[:numberOfNodes]]
        fbSubGraph = fbGraph.subgraph(nodes)
        sn = SocialNetwork(fbSubGraph)
        sn.recommendedFriends()

  def test_StressTestingFrom1000To20000NodesForRecommendedFriendsWithSortedDegreeData(self):
    dataset = downloadDataset()
    with open(dataset[1], 'rb') as f:
      fbGraph = pickle.load(f)
    for numberOfNodes in range(1000, 20000, 1000):
      nodes = [node for node in list(fbGraph.nodes())[:numberOfNodes]]
      fbSubGraph = fbGraph.subgraph(nodes)
      sn = SocialNetwork(fbSubGraph)
      sn.recommendedFriends()

  def test_StressTestingFrom1000To20000NodesForConnectingComunities(self):
    dataset = downloadDataset()
    with open(dataset[1], 'rb') as f:
      fbGraph = pickle.load(f)
    for numberOfNodes in range(1000, 20000, 1000):
      nodes = [node for node in list(fbGraph.nodes())[:numberOfNodes]]
      fbSubGraph = fbGraph.subgraph(nodes)
      sn = SocialNetwork(fbSubGraph)
      sn.connectCommunities()

  def test_StressTestingFrom1000To20000NodesForFindingImportantPeople(self):
    dataset = downloadDataset()
    with open(dataset[1], 'rb') as f:
      fbGraph = pickle.load(f)
    for numberOfNodes in range(1000, 20000, 1000):
      nodes = [node for node in list(fbGraph.nodes())[:numberOfNodes]]
      fbSubGraph = fbGraph.subgraph(nodes)
      sn = SocialNetwork(fbSubGraph)
      sn.findImportantPeople()

  def test_StressTestingFrom1000To20000NodesForFindingLargestCommunities(self):
    dataset = downloadDataset()
    with open(dataset[1], 'rb') as f:
      fbGraph = pickle.load(f)
    for numberOfNodes in range(1000, 20000, 1000):
      nodes = [node for node in list(fbGraph.nodes())[:numberOfNodes]]
      fbSubGraph = fbGraph.subgraph(nodes)
      sn = SocialNetwork(fbSubGraph)
      sn.findLargestCommunities()

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

  def test_FindRecommendedFriendsWithEmptyGraph(self):
    fbGraph = nx.Graph()
    sn = SocialNetwork(fbGraph)
    self.assertEqual([], sn.recommendedFriends())

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

  def test_FindImportantPeopleWithEmptyGraph(self):
    fbGraph = nx.Graph()
    sn = SocialNetwork(fbGraph)
    importantPeople = sn.findImportantPeople()
    self.assertEqual([], importantPeople)

  def test_ConnectCommunities(self):
    dataset = downloadDataset()
    with open(dataset[1], 'rb') as f:
      fbGraph = pickle.load(f)
    nodes = [node for node in list(fbGraph.nodes())[:1000]]
    fbSubGraph = fbGraph.subgraph(nodes)
    sn = SocialNetwork(fbSubGraph)
    cliques = sorted(nx.find_cliques(fbSubGraph), key=lambda x: len(x))
    largestClique = fbSubGraph.subgraph(set(cliques[-1])).copy()
    secondLargestClique = fbSubGraph.subgraph(set(cliques[-2])).copy()
    largestCliqueBetweenessCentrality = nx.betweenness_centrality(largestClique)
    secondLargestCliqueBetweenessCentrality = nx.betweenness_centrality(secondLargestClique)
    largestCliqueBottleneckUser = max(largestCliqueBetweenessCentrality, key=largestCliqueBetweenessCentrality.get)
    secondLargestCliqueBottleneckUser = max(secondLargestCliqueBetweenessCentrality, key=secondLargestCliqueBetweenessCentrality.get)
    expectedDistanceBetweenTwoUsers = sn.getDistanceWithCurrentNode(largestCliqueBottleneckUser, secondLargestCliqueBottleneckUser)

    self.assertEqual(expectedDistanceBetweenTwoUsers, sn.connectCommunities())

  def test_ConnectCommunitiesWithEmptyGraph(self):
    fbGraph = nx.Graph()
    sn = SocialNetwork(fbGraph)
    self.assertEqual(-1, sn.connectCommunities())

  def test_FindLargestCommunity(self):
    dataset = downloadDataset()
    with open(dataset[1], 'rb') as f:
      fbGraph = pickle.load(f)
    nodes = [node for node in list(fbGraph.nodes())[:1000]]
    fbSubGraph = fbGraph.subgraph(nodes)
    sn = SocialNetwork(fbSubGraph)
    largestClique = set(sorted(nx.find_cliques(fbSubGraph), key=lambda x: len(x))[-1])
    expectedFacebookLargestClique = fbSubGraph.subgraph(largestClique).copy()
    # Go out 1 degree of separation
    for node in list(expectedFacebookLargestClique.nodes()):
        expectedFacebookLargestClique.add_nodes_from(fbSubGraph.neighbors(node))
        expectedFacebookLargestClique.add_edges_from(zip([node]*len(list(fbSubGraph.neighbors(node))), fbSubGraph.neighbors(node)))

    self.assertIsNotNone(expectedFacebookLargestClique)
    self.assertEqual(expectedFacebookLargestClique.nodes(), sn.findLargestCommunities().nodes())

  def test_FindLargestCommunityWithEmptyGraph(self):
    fbGraph = nx.Graph()
    sn = SocialNetwork(fbGraph)
    self.assertIsNone(sn.findLargestCommunities())

  def test_ShortestPathBFS(self):
    dataset = downloadDataset()
    with open(dataset[1], 'rb') as f:
      fbGraph = pickle.load(f)
    nodes = [node for node in list(fbGraph.nodes())[:1000]]
    fbSubGraph = fbGraph.subgraph(nodes)
    sn = SocialNetwork(fbSubGraph)
    for node, _ in fbSubGraph.nodes(data=True):
      for neighbour  in fbSubGraph.neighbors(node):
        self.assertEqual(fbSubGraph.has_edge(node, neighbour), sn.pathExistBFS(node, neighbour))

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

  def test_ShortestPathWithEmptyGraph(self):
    fbGraph = nx.Graph()
    sn = SocialNetwork(fbGraph)
    for node, _ in fbGraph.nodes(data=True):
      for neighbour  in fbGraph.neighbors(node):
        if fbGraph.has_edge(node, neighbour):
          self.assertTrue((node, neighbour) in sn.traversePath)
    self.assertGreater(len(sn.traversePath), 0)

def runTests(testCase: TestSocialNetworkAnalysis, testMethod: str):
    suite = unittest.TestSuite()
    suite.addTest(testCase(testMethod))
    runner = unittest.TextTestRunner()
    runner.run(suite)

if __name__ == '__main__':
    stressTests = [
        'test_StressTestingFrom1000To20000NodesForRecommendedFriendsWithUnsortedData'
        'test_StressTestingFrom1000To20000NodesForRecommendedFriendsWithSortedDegreeData',
        'test_StressTestingFrom1000To20000NodesForConnectingComunities',
        'test_StressTestingFrom1000To20000NodesForFindingImportantPeople',
        'test_StressTestingFrom1000To20000NodesForFindingLargestCommunities'
    ]

    unitTests = [
        'test_FindRecommendedFriends',
        'test_ShortestPathWithEmptyGraph',
        'test_FindImportantPeople',
        'test_ConnectCommunities',
        'test_FindLargestCommunity',
        'test_ShortestPathBFS',
        'test_TraversePathWillAllNodes'
    ]

    with ThreadPoolExecutor() as executor:
        # Execute only the specified tests in parallel
        futures = [executor.submit(runTests, TestSocialNetworkAnalysis, test) for test in unitTests]
        for future in futures:
            future.result()
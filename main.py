import networkx as nx
import matplotlib as mpl
import matplotlib.pyplot as plt
from social_net import createSocialNet

# pathExistBFS will use breath first search
# https://www.geeksforgeeks.org/breadth-first-search-or-bfs-for-a-graph/#
# to determine if the path between two vertexes are connected in the shortest way possible
# Step 1: Begins with a node, traverses all its adjacent
# Step 2: Once all adjacent are visited, then their adjacent are traversed
# Time Complexity: O(v + e) (since its traverse through all vertex and edge in worst case)
def pathExistBFS(G: nx.DiGraph, startVertex: int, endVertex: int) -> bool:
  visited_nodes = set()
  # Begin traverse from the starting node
  queue = [startVertex]

  # Traverse all its adjacent node
  for node in queue:
      # Once all adjacent are visited, then their adjacent are traversed
      neighbors = G.neighbors(node)
      if endVertex in neighbors:
          print('Path exists between nodes {0} and {1}'.format(startVertex, endVertex))
          return True
      else:
          visited_nodes.add(node)
          queue.extend([n for n in neighbors if n not in visited_nodes])

      # Check to see if there are any vertex that can be reached from the current node adjacent
      # in order to know if there are any path that BFS can traverse
      if node == queue[-1]:
          print('Path does not exist between nodes {0} and {1}'.format(startVertex, endVertex))
          return False

if __name__ =="__main__":
  # Initialize an empty graph with the corresponding vertex
  createSocialNet()
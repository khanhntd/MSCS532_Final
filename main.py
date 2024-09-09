import networkx as nx
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
  G = nx.DiGraph()
  G.add_nodes_from([1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
  print("Graph vertex ", G.nodes())

  # Add the corresponding edge between vertex before calculating degree centrality
  for nearestVertex in range(2, len(G.nodes()) + 1 ):
    G.add_edge(1, nearestVertex)

  print("Graph egdes", G.edges())
  print("Vertex 1's neighbor", nx.degree_centrality(G))

  pathExistBFS(G, 1, 2)

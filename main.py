import sys
import pstats
import cProfile
from social_net import socialNetworkAnalysis

if __name__ =="__main__":
  profiler = 'profiler.prof'
  sys.setrecursionlimit(1000000)
  # Initialize an empty graph with the corresponding vertex
  socialNetworkAnalysis()
  #cProfile.run('socialNetworkAnalysis()', profiler)
  #p = pstats.Stats(profiler)
  #p.strip_dirs().sort_stats('cumulative').print_stats()


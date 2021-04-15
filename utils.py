def deltaToAdjMatrix(delta):
   M = dict()
   for state in delta:
      M[state] = set()
      for trans in delta[state]:
         M[state].add(trans[1])
   return M

def print_delta(d):
   for state in d:
      print(state)
      for trans in d[state]:
         print('\t', trans)
   
def print_adjMatrix(M):
   for item in M:
      print(item+":",M[item])

def DFS(G, u, v, visited):
   if u == v:
      return True
   if visited[u] == True:
      return False
   visited[u] = True
   for node in G[u]:
      canReachV = DFS(G, node, v, visited)
      if canReachV == True:
         return True
   return False
   
def print_minTable(table):
   for st1 in table:
      print(st1)
      for st2 in table[st1]:
         print('\t'+st2+':',table[st1][st2])
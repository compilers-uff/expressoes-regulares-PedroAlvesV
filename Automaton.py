# Epsilon
E = "_e"

class Automaton:
   
   def __init__(self, sigma, Q, delta, ini, F):
      self.sigma = sigma
      self.Q = Q
      self.delta = delta
      self.ini = ini
      self.F = F
   
   def print_delta(self):
      for state in self.delta:
         print(state)
         for trans in self.delta[state]:
            print('\t', trans)
   
   def __str__(self):
      print("Sigma:", self.sigma)
      print("Q:", self.Q)
      print("Delta:")
      self.print_delta()
      print("Initial state:", self.ini)
      print("Final states:", self.F)
      return ""

   def concat_automata(self, a):
      # Combina sigmas
      sigma = self.sigma | a.sigma
      # Renomeia estados em Q e F
      for i, state in enumerate(self.Q):
         self.Q[i] = state+"1"
      self.ini += "1"
      for i, state in enumerate(self.F):
         self.F[i] = state+"1"
      for i, state in enumerate(a.Q):
         a.Q[i] = state+"2"
      a.ini += "2"
      for i, state in enumerate(a.F):
         a.F[i] = state+"2"
      # Combina estados
      Q = self.Q + a.Q
      # Renomeia estados em delta, renomeia estados em transições e combina deltas
      delta = {}
      for state in self.delta:
         delta[state+"1"] = []
         for i, trans in enumerate(self.delta[state]):
            new_trans = (trans[0], trans[1]+"1")
            self.delta[state][i] = new_trans
            delta[state+"1"].append(new_trans)
      for state in a.delta:
         delta[state+"2"] = []
         for i, trans in enumerate(a.delta[state]):
            new_trans = (trans[0], trans[1]+"2")
            a.delta[state][i] = new_trans
            delta[state+"2"].append(new_trans)
      # Adiciona transição nova
      for i, state in enumerate(self.F): 
         delta[state].append((E, a.ini))
      return Automaton(sigma, Q, delta, self.ini, a.F)

   def sum_automata(self, a):
      # Combina sigmas
      sigma = self.sigma | a.sigma
      # Renomeia estados em Q e F
      for i, state in enumerate(self.Q):
         self.Q[i] = state+"1"
      self.ini += "1"
      for i, state in enumerate(self.F):
         self.F[i] = state+"1"
      for i, state in enumerate(a.Q):
         a.Q[i] = state+"2"
      a.ini += "2"
      for i, state in enumerate(a.F):
         a.F[i] = state+"2"
      # Combina estados
      Q = self.Q + a.Q
      # Renomeia estados em delta, renomeia estados em transições e combina deltas
      delta = {}
      for state in self.delta:
         delta[state+"1"] = []
         for i, trans in enumerate(self.delta[state]):
            new_trans = (trans[0], trans[1]+"1")
            self.delta[state][i] = new_trans
            delta[state+"1"].append(new_trans)
      for state in a.delta:
         delta[state+"2"] = []
         for i, trans in enumerate(a.delta[state]):
            new_trans = (trans[0], trans[1]+"2")
            a.delta[state][i] = new_trans
            delta[state+"2"].append(new_trans)
      # Adiciona estados novos
      Q.append('q0')
      Q.append('qf')
      delta['qf'] = []
      # Adiciona transições novas
      delta['q0'] = [(E, self.ini), (E, a.ini)]
      for i, state in enumerate(self.F): 
         delta[state].append((E, 'qf'))
      for i, state in enumerate(a.F): 
         delta[state].append((E, 'qf'))
      return Automaton(sigma, Q, delta, 'q0', ['qf'])

   def multiply_automaton(self):
      # Renomeia estados em Q, F e delta
      for i, state in enumerate(self.Q):
         self.Q[i] = state+"1"
      self.ini += "1"
      for i, state in enumerate(self.F):
         self.F[i] = state+"1"
      delta = {}
      for state in self.delta:
         delta[state+"1"] = []
         for i, trans in enumerate(self.delta[state]):
            new_trans = (trans[0], trans[1]+"1")
            delta[state+"1"].append(new_trans)
      self.delta = delta
      # Adiciona estados novos
      self.Q.append('q0')
      self.Q.append('qf')
      self.delta['qf'] = []
      # Adiciona transições novas
      self.delta['q0'] = [(E, self.ini), (E, 'qf')]
      for i, state in enumerate(self.F): 
         self.delta[state].append((E, 'qf'))
         self.delta[state].append((E, self.ini))
      self.ini = 'q0'
      self.F = ['qf']
      return self
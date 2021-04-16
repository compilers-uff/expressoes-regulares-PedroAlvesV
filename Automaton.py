import utils

# Epsilon
E = "_e"

class Automaton:
   
   e_closure_table = None
   
   def __init__(self, sigma, Q, delta, ini, F):
      self.sigma = sigma
      self.Q = Q
      self.delta = delta
      self.ini = ini
      self.F = F
   
   def __str__(self):
      print("Sigma:", self.sigma)
      print("Q:", self.Q)
      print("Delta:")
      utils.print_delta(self.delta)
      print("Initial state:", self.ini)
      print("Final states:", self.F)
      if self.e_closure_table:
         for state in self.Q:
            print("e-closure("+state+") =", self.e_closure_table[state])
      return ""
   
   def simplify_state_names(self):
      alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
      names_map = dict()
      delta = dict()
      for i, state in enumerate(self.Q):
         names_map[state] = alphabet[i]
      for state in self.delta:
         delta[names_map[state]] = []
         for trans in self.delta[state]:
            delta[names_map[state]].append( (trans[0], names_map[trans[1]]) )
            
      Q = list(names_map.values())
      ini = names_map[self.ini]
      F = []
      for state in self.F:
         F.append(names_map[state])

      return Automaton(self.sigma, Q, delta, ini, F)
         
   def accepted(self, word):
      return self.delta_star(self.ini, word) in self.F
   
   def delta_star(self, ini, word, debug=False):
      current_state = ini
      for symbol in word:
         transited = False
         for trans in self.delta[current_state]:
            if trans[0] == symbol:
               if debug: print(f"d({current_state}, {symbol}) = {trans[1]}")
               current_state = trans[1]
               transited = True
               break
         if not transited:
            return "__NOTRANSITION__"
      return current_state
      
   def compute_e_closures(self):
      t = {}
      total = 0
      # Começa computando transições epsilon diretas e o próprio estado
      for state in self.delta:
         t[state] = {state}
         total += 1
         for trans in self.delta[state]:
            if trans[0] == E:
               t[state].add(trans[1])
               total += 1
      # Computa estados indiretamente alcançados por epsilon
      # Injeta estados alcançáveis por estados já computados uma vez por repetição
      # Para quando o total de estados em todas as closures para de crescer
      comp = total
      while True:
         for state in t:
            temp = set()
            for reach1 in t[state]:
               if reach1 != state:
                  for reach2 in t[reach1]:
                     if reach2 not in t[state]:
                        temp.add(reach2)
                        comp += 1
            t[state] |= temp
         if comp == total:
            break
         total = comp
      self.e_closure_table = t
   
   def e_closure(self, state):
      if state not in self.Q:
         return None
      return self.e_closure_table[state]

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
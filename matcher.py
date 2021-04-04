from collections import deque
from Automaton import Automaton 

# Epsilon
E = "_e"

def min_automaton(s):
   d = { 'q0': [(s, 'q1')], 'q1': [] }
   return Automaton({s}, ['q0','q1'], d, 'q0', ['q1'])

def concat_automata(a1, a2):
   # Combina sigmas
   sigma = a1.sigma | a2.sigma
   # Renomeia estados em Q e F
   for i, state in enumerate(a1.Q):
      a1.Q[i] = state+"1"
   a1.ini += "1"
   for i, state in enumerate(a1.F):
      a1.F[i] = state+"1"
   for i, state in enumerate(a2.Q):
      a2.Q[i] = state+"2"
   a2.ini += "2"
   for i, state in enumerate(a2.F):
      a2.F[i] = state+"2"
   # Combina estados
   Q = a1.Q + a2.Q
   # Renomeia estados em delta, renomeia estados em transições e combina deltas
   delta = {}
   for state in a1.delta:
      delta[state+"1"] = []
      for i, trans in enumerate(a1.delta[state]):
         new_trans = (trans[0], trans[1]+"1")
         a1.delta[state][i] = new_trans
         delta[state+"1"].append(new_trans)
   for state in a2.delta:
      delta[state+"2"] = []
      for i, trans in enumerate(a2.delta[state]):
         new_trans = (trans[0], trans[1]+"2")
         a2.delta[state][i] = new_trans
         delta[state+"2"].append(new_trans)
   # Adiciona transição nova
   for i, state in enumerate(a1.F): 
      delta[state].append((E, a2.ini))
   return Automaton(sigma, Q, delta, a1.ini, a2.F)

def sum_automata(a1, a2):
   # Combina sigmas
   sigma = a1.sigma | a2.sigma
   # Renomeia estados em Q e F
   for i, state in enumerate(a1.Q):
      a1.Q[i] = state+"1"
   a1.ini += "1"
   for i, state in enumerate(a1.F):
      a1.F[i] = state+"1"
   for i, state in enumerate(a2.Q):
      a2.Q[i] = state+"2"
   a2.ini += "2"
   for i, state in enumerate(a2.F):
      a2.F[i] = state+"2"
   # Combina estados
   Q = a1.Q + a2.Q
   # Renomeia estados em delta, renomeia estados em transições e combina deltas
   delta = {}
   for state in a1.delta:
      delta[state+"1"] = []
      for i, trans in enumerate(a1.delta[state]):
         new_trans = (trans[0], trans[1]+"1")
         a1.delta[state][i] = new_trans
         delta[state+"1"].append(new_trans)
   for state in a2.delta:
      delta[state+"2"] = []
      for i, trans in enumerate(a2.delta[state]):
         new_trans = (trans[0], trans[1]+"2")
         a2.delta[state][i] = new_trans
         delta[state+"2"].append(new_trans)
   # Adiciona estados novos
   Q.append('q0')
   Q.append('qf')
   delta['qf'] = []
   # Adiciona transições novas
   delta['q0'] = [(E, a1.ini), (E, a2.ini)]
   for i, state in enumerate(a1.F): 
      delta[state].append((E, 'qf'))
   for i, state in enumerate(a2.F): 
      delta[state].append((E, 'qf'))
   return Automaton(sigma, Q, delta, 'q0', ['qf'])

def multiply_automaton(a):
   # Renomeia estados em Q, F e delta
   for i, state in enumerate(a.Q):
      a.Q[i] = state+"1"
   a.ini += "1"
   for i, state in enumerate(a.F):
      a.F[i] = state+"1"
   delta = {}
   for state in a.delta:
      delta[state+"1"] = []
      for i, trans in enumerate(a.delta[state]):
         new_trans = (trans[0], trans[1]+"1")
         delta[state+"1"].append(new_trans)
   a.delta = delta
   # Adiciona estados novos
   a.Q.append('q0')
   a.Q.append('qf')
   a.delta['qf'] = []
   # Adiciona transições novas
   a.delta['q0'] = [(E, a.ini), (E, 'qf')]
   for i, state in enumerate(a.F): 
      a.delta[state].append((E, 'qf'))
      a.delta[state].append((E, a.ini))
   a.ini = 'q0'
   a.F = ['qf']
   return a

op = ['.', '+', '*']

def parse(tokens, automaton=None):
   token=tokens.popleft()
   if token in op:
      if token=='.':
         t1, a1 = parse(tokens, automaton)
         t2, a2 = parse(tokens, automaton)
         aF = concat_automata(a1, a2)
         return t1+t2, aF
      elif token=='+':
         t1, a1 = parse(tokens, automaton)
         t2, a2 = parse(tokens, automaton)
         aF = sum_automata(a1, a2)
         return "("+t1+"+"+t2+")", aF
      elif token=='*':
         t, a = parse(tokens, automaton)
         a = multiply_automaton(a)
         return t+"*", a
   else:
      a = min_automaton(token)
      return token, a

def erToAFNe(er, debug=False):
   infix, afne = parse(deque(er.split()))
   if debug:
      print("Input:", infix)
      print("\nAFNe:")
      print(afne)
   return afne

erToAFNe("* + . a a . b b", True)
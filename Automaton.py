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
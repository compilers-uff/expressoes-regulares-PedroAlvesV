from collections import deque
from Automaton import Automaton 

def min_automaton(s):
   d = { 'q0': [(s, 'q1')], 'q1': [] }
   return Automaton({s}, ['q0','q1'], d, 'q0', ['q1'])

op = ['.', '+', '*']

def parse(tokens, automaton=None):
   token=tokens.popleft()
   if token in op:
      if token=='.':
         t1, a1 = parse(tokens, automaton)
         t2, a2 = parse(tokens, automaton)
         aF = a1.concat_automata(a2)
         return t1+t2, aF
      elif token=='+':
         t1, a1 = parse(tokens, automaton)
         t2, a2 = parse(tokens, automaton)
         aF = a1.sum_automata(a2)
         return "("+t1+"+"+t2+")", aF
      elif token=='*':
         t, a = parse(tokens, automaton)
         a.multiply_automaton()
         return t+"*", a
   else:
      a = min_automaton(token)
      return token, a

def erToAFNe(er, print_input=False):
   er = er.replace('(',' ').replace(',',' ').replace(')',' ')
   infix, afne = parse(deque(er.split()))
   afne.compute_e_closures()
   if print_input:
      print("Input:", infix)
   return afne
   
'''
afne = erToAFNe("* + . a a . b b", True)
#afne = erToAFNe("+ a b", True)
print("\n####################### AFNe:")
#print(afne)
afn = afne.afneToAFN()
print("\n####################### AFN:")
#print(afn)
afd = afn.afnToAFD()
print("\n####################### AFD:")
#print(afd)
afd = afd.simplify_state_names()
afdMin = afd.afdToAFDmin()
print("\n####################### AFD mínimo:")
print(afdMin)
'''


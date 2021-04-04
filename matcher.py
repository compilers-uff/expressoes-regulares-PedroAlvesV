from Automaton import Automaton

delta = {
   'q0': [('0', 'q0'), ('1', 'q1')],
   'q1': [('0', 'q0'), ('1', 'q2')],
   'q2': [('0', 'q3'), ('1', 'q2')],
   'q3': [('0', 'q3'), ('1', 'q3')],
}

A = Automaton(['0','1'], ['q0','q1','q2','q3'], delta, 'q0', ['q3'])
print(A)
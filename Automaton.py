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
         for trans in self.delta[current_state]:
            if trans[0] == symbol:
               if debug: print(f"d({current_state}, {symbol}) = {trans[1]}")
               current_state = trans[1]
               break
      return current_state
   
   def afdToAFDmin(self):
      # Criação da tabela de minimização
      table = dict()
      sets = dict()
      for i, st1 in enumerate(self.Q):
         if i==len(self.Q)-1: break
         table[st1] = dict()
         sets[st1] = dict()
         for j, st2 in enumerate(self.Q):
            if j<=i: continue
            table[st1][st2] = False
            sets[st1][st2] = set()
      
      # Marcação dos estados trivialmente não-equivalentes
      for st1 in table:
         for st2 in table[st1]:
            if (st1 in self.F and st2 not in self.F) or (st1 not in self.F and st2 in self.F):
               table[st1][st2] = True

      # Propagação recursiva da marcação
      def propagate_mark(qu, qv):
         for pair in sets[qu][qv]:
            pu, pv = pair[0], pair[1]
            if not pu in table or not pv in table[pu]:
               pu, pv = pv, pu
            table[pu][pv] = True
            if sets[pu][pv]:
               propagate_mark(pu, pv)

      # Marcação dos estados não-equivalentes
      for qu in table:
         for qv in table[qu]:
            if not table[qu][qv]:
               for symbol in self.sigma:
                  pu = None
                  pv = None
                  for trans in self.delta[qu]:
                     if trans[0] == symbol:
                        pu = trans[1]
                  for trans in self.delta[qv]:
                     if trans[0] == symbol:
                        pv = trans[1]
                  #print(f"\nd({qu}, {symbol}) = {pu}")
                  #print(f"d({qv}, {symbol}) = {pv}")
                  if pu != pv:                           # Caso 1 (pu e pv iguais): não marcar
                     if not pu in table or not pv in table[pu]:
                        pu, pv = pv, pu
                     if not table[pu][pv]:               # Caso 2 ({pu, pv} não marcado): 
                        sets[pu][pv].add((qu, qv))       #     incluir {qu, qv} na lista em {pu, pv}
                     else:                               # Caso 3 ({pu, pv} marcado): 
                        table[qu][qv] = True             #     marcar {qu, qv}
                        if sets[qu][qv]:                 #     e propagar
                           propagate_mark(qu,qv)
                           
      #utils.print_minTable(table)
   
      # Unificação dos estados equivalentes
      # Gera um mapa de fusões inicial
      merge_map = dict()
      for st1 in table:
         merge_map[st1] = set()
         for st2 in table[st1]:
            merge_map[st2] = set()
            if not table[st1][st2]:
               merge_map[st1].add(st2)

      # Remove duplicatas do mapa
      for st1 in merge_map:
         for st2 in merge_map.keys():
            if st1 != st2 and merge_map[st1] and merge_map[st2]:
               if merge_map[st1].intersection(merge_map[st2]):
                  merge_map[st1].update(merge_map[st2])
                  merge_map[st2] = set()
            
      # Uniformiza projeções no mapa
      for state in self.Q:
         if state in merge_map:
            for old_state in merge_map[state]:
               merge_map[old_state] = {state} | merge_map[state]
                  
      # Altera formato do mapa e tipos, criando uma relação <estado original>:<estado resultante> de string pra string
      for state in merge_map:
         if merge_map[state]:
            merge_map[state] = "".join(merge_map[state])
         else:
            merge_map[state] = state
               
      # Corrige transições
      for state in self.delta:
         for i in range(len(self.delta[state])):
            trans = self.delta[state][i]
            if trans[1] in merge_map:
               self.delta[state][i] = (trans[0], merge_map[trans[1]])
      
      # Adiciona estados combinados a delta e remove registros estados originais
      delta = dict()
      for state in merge_map:
         delta[merge_map[state]] = self.delta[state]
      
      self.Q = list(delta.keys())
      
      # Corrige estado inicial e estados finais
      self.ini = merge_map[self.ini]
      for i, state in enumerate(self.F):
         self.F[i] = merge_map[state]
      self.F = list(set(self.F))
      
      def is_d(state):
         if state in self.F or state == self.ini:
            return False
         for trans in delta[state]:
            if trans[1] != state:
               return False
         return True
      
      # Remove possível estado 'd' (criado para totalizar função programa)
      d_states = set()
      for state in self.Q:
         if is_d(state):
            del delta[state]
            d_states.add(state)
      for state in delta:
         for i in range(len(delta[state])):
            trans = delta[state][i]
            if trans[1] in d_states:
               delta[state].remove(trans)
      
      del self.delta
      self.delta = delta
      
      self.Q = list(self.delta.keys())
      
      return self
   
   def afnToAFD(self):
      d = self.delta.copy()
      F = set(self.F)
      
      # Histórico de estados criados nesse processo. Guarda <estado>:<estados originais> (ex.: '51': {'5','1'})
      # É necessário pra prevenir estados duplicados (ex.: '51' e '15') criados em momentos diferentes.
      new_states = dict()
            
      def is_duplicate(st_components, statelist, find=False):
         for state, components in statelist.items():
            if st_components == components:
               if find:
                  return state
               return True
         return False
         
      def is_final(mother_states):
         for state in mother_states:
            if state in self.F:
               return True
         return False
      
      # Resolve indeterminismo inicial (leitura de símbolo num estado podendo levar a mais de um outro)
      for state in self.delta:
         # print("-------------")
         # utils.print_delta(d)
         for i in range(len(self.delta[state])):
            trans = self.delta[state][i]
            # Sendo a transição indeterminística, aglutina estados de destino num único estado novo
            if len(trans[1]) > 1:
               new_state = ''.join(trans[1])
               trans_symbol = trans[0]
               mother_states = trans[1]
               # Adiciona à lista de estados finais, se for gerado a partir de algum estado final
               if is_final(mother_states):
                  F.add(new_state)
               new_transitions = []
               # Avalia transições desse novo estado e acrescenta entrada (estado e transições) em delta
               # Prepara, também, informações sobre estados novos criados como destino das transições novas
               for symbol in self.sigma:
                  dest_new_state = ''
                  dest_mother_states = set()
                  for mother_state in mother_states:
                     for t in self.delta[mother_state]:
                        if t[0] == symbol:
                           new_state_component_candidate = ''.join(t[1])
                           if dest_new_state != new_state_component_candidate:
                              dest_new_state += ''.join(t[1])
                              temp = t[1]
                              if isinstance(t[1], str):
                                 temp = {temp}
                              dest_mother_states |= temp
                  if dest_new_state == '':
                     continue
                  # Previne duplicação de estados novos com nomes diferentes (concatenações diferentes)
                  state_name = is_duplicate(dest_mother_states, new_states, True)
                  if state_name and state_name != dest_new_state:
                     dest_new_state = state_name
                  # Adiciona à lista de estados finais, se for gerado a partir de algum estado final
                  if is_final(dest_mother_states):
                     F.add(dest_new_state)
                  new_trans = (symbol, dest_new_state)
                  new_transitions.append(new_trans)
                  # Guarda estados criados como destino de estados novos
                  new_states[dest_new_state] = dest_mother_states
               d[new_state] = new_transitions
               # Atualiza transição indeterminística antiga
               d[state][i] = (trans_symbol, new_state)
               # Guarda guarda estados novos
               new_states[new_state] = mother_states
            else:
               # Atualiza transições já determinísticas (questão de tipo, convertendo de set para string)
               d[state][i] = (trans[0], ''.join(trans[1]))
            
      # Como não é garantida a ordem de concatenação na criação de novos estados,
      # é possível que new_states contenha estados duplicados nomeados diferentes (ex.: q0q1 e q1q0)
      # Comparando os estados que deram origem a eles, é simples eliminá-los
      def eliminate_duplicates(states):
         res = dict()
         for state, components in states.items():
            if not is_duplicate(components, res):
               res[state] = components
         return res
      
      # Criação de estados novos a partir de transições criadas no passo anterior
      # Algoritmo quase idêntico ao trecho do passo anterior. Difere, principalmente,
      # na repetição enquanto o tamanho da tabela de transições crescer.
      dlen = -1
      while dlen != len(d):
         dlen = len(d)
         
         new_states = eliminate_duplicates(new_states)
         
         states_to_add = new_states.copy()
         for state, mother_states in states_to_add.items():
            new_transitions = []
            for symbol in self.sigma:
               dest_new_state = ''
               dest_mother_states = set()
               for mother_state in mother_states:
                  for trans in d[mother_state]:
                     if trans[0] == symbol:
                        new_state_component_candidate = ''.join(trans[1])
                        if dest_new_state != new_state_component_candidate:
                           dest_new_state += ''.join(trans[1])
                           dest_mother_states.add(trans[1])
               if dest_new_state == '':
                  continue
               state_name = is_duplicate(dest_mother_states, new_states, True)
               if state_name and state_name != dest_new_state:
                  dest_new_state = state_name
               if is_final(dest_mother_states):
                  F.add(dest_new_state)
               new_trans = (symbol, dest_new_state)
               new_transitions.append(new_trans)
               new_states[dest_new_state] = dest_mother_states
            d[state] = new_transitions
            
      # Remoção de estados inalcançáveis
      unreachable = set()
      
      graph = utils.deltaToAdjMatrix(d)
      visited = dict()
      
      for state in d:
         for node in graph:
            visited[node] = False
         if not utils.DFS(graph, self.ini, state, visited):
            unreachable.add(state)
      
      for state in unreachable:
         del d[state]
         
      F = F - unreachable
      
      Q = list(d.keys())
      F = list(F)
      
      # Totaliza AFD
      incomplete_states = set()
      for state in d:
         if len(d[state]) < len(self.sigma):
            incomplete_states.add(state)
         elif len(d[state]) > len(self.sigma):
            print("!!!!!!!!!!!!!!!!!")
      
      if incomplete_states:
         new_state_d = "_d"
         Q.append(new_state_d)
         d[new_state_d] = []
         for symbol in self.sigma:
            d[new_state_d].append((symbol, new_state_d))
         for state in incomplete_states:
            missing_trans = self.sigma.copy()
            for trans in d[state]:
               if trans[0] in missing_trans:
                  missing_trans.remove(trans[0])
            for symbol in missing_trans:
               d[state].append((symbol, new_state_d))
               
      return Automaton(self.sigma, Q, d, self.ini, F)
   
   def afneToAFN(self):
      self.compute_e_closures()
      d = dict()
      F = set()
      for state in self.Q:
         # Definindo d'
         d[state] = []
         for symbol in self.sigma:
            temp = []
            for reachable in self.e_closure_table[state]:
               # Definindo F' (aproveitando o loop pelos e_closure)
               if reachable in self.F:
                  F.add(state)
               for trans in self.delta[reachable]:
                  if trans[0] == symbol:
                     temp.append(self.e_closure_table[trans[1]])
                     break
            tempset = set().union(*temp)
            if tempset:
               d[state].append( (symbol, tempset) )
      F = list(F)
      return Automaton(self.sigma, self.Q, d, self.ini, F)

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
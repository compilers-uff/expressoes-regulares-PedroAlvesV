from collections import deque
from Automaton import Automaton 
import utils
import sys

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
   er = er.replace('(',' ').replace(',',' ').replace(')',' ').replace('\'','')
   infix, afne = parse(deque(er.split()))
   afne.compute_e_closures()
   if print_input:
      print("Input:", infix)
   return afne

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
            delta[state][i] = "rm"
      delta[state] = [trans for trans in delta[state] if trans != "rm"]
   
   del self.delta
   self.delta = delta
   
   self.Q = list(self.delta.keys())
   
   return self


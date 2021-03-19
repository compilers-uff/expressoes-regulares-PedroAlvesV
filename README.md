# Expressões regulares

## Objetivo

Implemente em Python 3 um _matcher_ de expressões regulares. Dada uma expressão regular e uma palavra, sua implementação deve dizer **OK** ou **Not OK** quando a palavra dada "casa" com a expressão regular dada.

## Implementação 

- Sua implementação deve ser organizada da seguinte forma e deve sempre implementar os algoritmos descritos no livro-texto da disciplina.

1. Transformador de expressões regulares (ER) à autômatos finitos não-determinísticos com transições vazias (AFNe).  

   A função `erToAFNe : ER -> AFNe` deve receber uma expressão regular pré-fixadas e retornar um AFNe que reconheça palavras que "casam" com a expressão regular e somente estas. 
   
   Uma expressão regular pré-fixada é dada, por exemplo por `+(.(a, b), c)`, representando a ER `ab + c`.
   
   O transformador deve implementar o algoritmo definido no livro-texto.
   
   Represente a função de transição `delta` como um dicionário em Python 3 onde as chaves são strings representando os estados de origem e os valores são pares de string e conjunto de string representando, respectivamente, um símbolo do alfabeto ou epsilon, e os estados alcançáveis através daquele símbolo. 

1. Transformador de AFNe à autômatos finitos não-determinísitcos (AFN).  

   A função `afneToAFD : AFNe -> AFN` deve receber um AFNe como descrito acima e produzir um AFN, representado como no item acima porém não permitindo que epsilon seja parâmtro atual de `delta`.
   
1. Transformador de AFN à AFD.  

    A função `afntoAFD : AFN -> AFD` deve receber um AFN e produzir o AFD associado. Utiliza a mesma representação para `delta` acima porém com a restrição de que os valores do dicionário, que representa `delta`, são pares com uma string como primeira projeção e conjunto de string como segunda. A cardinalidade do conjunto da segunda projeção é sempre 1. 
    
1. Transformador de AFD para AFD mínimo.

   A função `afdToAFDmin : AFD -> AFD` deve receber um AFD como descrito acima e retornar o AFD mínimo associado utilizado o algoritmo de minimização descrito no livro-texto.
   
1. Simiulador de AFD.

   Seja `A = (Sigma, Q, delta, q0, F)` um AFD.  A expressão Booleana `A.delta*(q0, w) in A.F`, em Python 3, é verdadeira quando `w` é aceita por `A` e falsa casa contrário. O predicado `A.accepted(w)` é verdadeiro quando `w` é aceita por `A`.
   
1. Um _matcher_ de ER.  

   A expressão booleana `match(er, w)`, onde `er` é uma expressão Booleana pré-fixada, como em 1., e `w` é uma string no alfabeto de `er` é verdadeira quando `w` "casa" com `er` e falsa caso contrário. O predicado `match: (er : ER) x (w : Sigma*) -> Bool` é definido como `afdToAFDmin(afnToAFD(afneToAFN(erToAFNe(er)))).accepted(w)`.
  
- Seu programa, `er.py`, deve ler uma ER prefixada da linha de comando ou várias a partir de um arquivo imprimindo "OK" ou "Not OK" dependendo dos parâmtros passados.
```shell  
python3 er.py "+( 'a', 'b')" "a"
python3 er.py -f ex1.er "a" 
```
Quando um arquivo for passado por parâmetro, as expressões regulares contidas neste arquivo devem ser verificadas contra a palavra passada por parâmetro.
Por exemplo, se o arquivo `ex1.er` contiver as expressões regulares
```
+(a,b)
.(a,b)
*(+(a, b))
```
e a chamada ao seu programa for
```
python3 er.py -f ex1.er "a"
```
seu programa deve imprimir as saídas abaixo.
```
match(+(a,b), a) == OK
match(.(a,b), a) == Not OK
match(*(+(a, b)), a) == OK
```
  
## Testes

Implemente os testes a seguir como predicados a serem executados pelo autograder, seguindo uma das formas de chamada ao seu programa descrita acima.

1. `match('a', 'a') == OK`
1. `match(+('a', 'b'), 'a') == OK`
2. `match(.('a', 'b'), 'ab') == OK`
3. `match(*(+(`a`, `b`), 'a') == OK`
4. `match(*(+(`a`, `b`), 'aaa') == OK`
5. `match(*(+(`a`, `b`), 'ab') == OK`
6. `match(*(+(`a`, `b`), 'aba') == OK`
7. `match(*(+(`a`, `b`), 'abababa') == OK`
8. Outros exemplos de expressões regulares mais complexas.

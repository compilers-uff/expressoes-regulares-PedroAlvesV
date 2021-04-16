import er

def test_er():
   assert er.match("a", "a")
   assert er.match("+(a,b)", "a")
   assert er.match("+(a,b)", "ab") == False
   assert er.match("*(+(a,b))", "a")
   assert er.match("*(+(a,b))", "aaa")
   assert er.match("*(+(a,b))", "ab")
   assert er.match("*(+(a,b))", "aba")
   assert er.match("*(+(a,b))", "abababa")
   assert er.match("*(+(.(a,b),.(c,d)))", "ab")
   assert er.match("*(+(.(a,b),.(c,d)))", "cd")
   assert er.match("*(+(.(a,b),.(c,d)))", "ac") == False
   assert er.match("*(+(.(a,b),.(c,d)))", "db") == False
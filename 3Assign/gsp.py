"""
Predicates:
----------
 on(X, Y)   -> stack(X, Y)
 onTable(X) -> putDown(X)
 clear(X)   -> stack(X, Y) | unStack(?Z, X) **
 holding(X) -> pickup(X) | unStack(X, ?Z) **
 armEmpty() -> putDown(?Z) | stack(?X, ?Y) **

===========

Actions:
-------
 pickup(X):
  P: onTable(X) && clear(X) && armEmpty()
  A: holding(X)
  D: onTable(X) && armEmpty()
  
 putDown(X):
  P: holding(X)
  A: onTable(X) && armEmpty()
  D: holding(X)

 unStack(X, Y):
  P: on(X, Y) && clear(X) && armEmpty()
  A: holding(X) && clear(Y)
  D: on(X, Y) && armEmpty()

 stack(X, Y):
  P: holding(X) && clear(Y)
  A: on(X, Y) && clear(X) && armEmpty()
  D: holding(X) && clear(Y)

Preidcate format: 
 ('predicate', ('on', 'X', 'Y'))

Conjunct format:
 ('conjunct', [('predicate', ('on', 'X', 'Y')), ('predicate', ('clear', 'X'))])

Action format:
 ('action', ('pickup', 'X'))

"""

currentState = {
    'on': [],
    'onTable': ['A'],
    'clear': ['B'],
    'holding': [],
    'armEmpty': True
    }

actionStore = {
    'pickup' : {
        'P' : [('onTable', '_0'), ('clear', '_0'),  ('armEmpty',)],
        'A' : [('holding', '_0')],
        'D' : [('onTable', '_0'), ('armEmpty',)]
        },

    'putDown' : {
        'P' : [('holding', '_0')],
        'A' : [('onTable', '_0'), ('armEmpty',)],
        'D' : [('holding', '_0')]
        },

    'unStack' : {
        'P' : [('on', '_0', '_1'), ('clear', '_0'), ('armEmpty',)],
        'A' : [('holding', '_0'), ('clear', '_1')],
        'D' : [('on', '_0', '_1'), ('armEmpty',)]
        },
    'stack' : {
        'P' : [('holding', '_0'), ('clear', '_1')],
        'A' : [('on', '_0', '_1'), ('clear', '_0'), ('armEmpty',)],
        'D' : [('holding', '_0'), ('clear', '_1')]
        }
    }

stack = []
plan = []

def generateConjunct(preCondList, args):
    c = []
    for p in preCondList:
        t = []
        t.append(p[0])
        for a in p[1:]:
            print a
            t.append(args[int(a[1])])
        t1 = tuple(t)
        c.append(tuple(['predicate', t1]))
    return c


def pushal(conjunct):
    stack.append(conjunct)
    for p in conjunct[1]:
        stack.append(p)

def progress(action):

    name = action[1][0]
    args = action[1][1:]
    
    add = actionStore[name]['A']
    for a in add:
        if a[0] == 'on': # two args, put as tuple
            currentState[a[0]].append(tuple([args[int(a[1][1])], args[int(a[2][1])]]))
        elif a[0] == 'armEmpty':
            currentState[a[0]] = True
        else: # one arg
            currentState[a[0]].append(args[int(a[1][1])])
            
    delete = actionStore[name]['D']
    for d in delete:
        
        if d[0] == 'on':
            currentState[d[0]].remove(tuple(args))
        elif d[0] == 'armEmpty':
            currentState[d[0]] == False
        else:
            currentState[d[0]].remove(args[int(d[1][1])])
            
    plan.append(action[1])

def getConjuct(pred): # TODO
    p = pred[1]
    return generateConjunct() 

def handle_predicate(pred):
    pass

def isInState(pred):
    p = pred[1]
    name = p[0]
    if name == 'on':
        return p[1:] in currentState[name]
    elif name == 'armEmpty':
        return currentState[name]
    else:
        return p[1:] in currentState[name]

def handle_conjuct(c):
    preds = c[1] # predicates of the conjunct
    for p in preds:
        if not isInState(p):
            pushal(c)
            break

def gsp():
    while len(stack) != 0:
        e = stack.pop()
        if e[0] == 'action':
            progress(e)
        elif e[0] == 'predicate':
            if not handle_predicate(e):
                return False
        else: # conjunct
            handle_conjuct(e)
    return True

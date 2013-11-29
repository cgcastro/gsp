"""
Predicates:
----------
 on(X, Y)   -> stack(X, Y)
 onTable(X) -> putDown(X)
 clear(X)   -> stack(X, ?Y) | unStack(?Z, X) **
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

Predicate format: 
 ('predicate', ('on', 'X', 'Y'))

Conjunct format:
 ('conjunct', [('predicate', ('on', 'X', 'Y')), ('predicate', ('clear', 'X'))])

Action format:
 ('action', ('pickup', 'X'))

"""

counter = 0

blockList = ['A', 'B', 'C', 'D']
#blockList = ['A', 'B']
#blockList = ['A',]
"""
ss = {
    'on': [('A', 'B'), ('B','C')],
    'onTable': ['C'],
    'clear': ['A'],
    'holding': [],
    'armEmpty': True
    }
"""
ss = {
    'on': [('C', 'A'), ('A', 'B')],
    'onTable': ['B'],
    'clear': ['C'],
    'holding': [],
    'armEmpty': True
    }

gg = {
    'on': [],
    'onTable': ['A', 'B', 'C',],
    'clear': ['A', 'B', 'C'],
    'holding': [],
    'armEmpty': True
    }


"""
gg = {
    'on': [ ('B', 'A'), ('C', 'B'),],
    'onTable': ['A',],
    'clear': [ 'C'],
    'holding': [],
    'armEmpty': True
    }
"""
"""
gg = {
    'on': [],
    'onTable': ['C', 'B', 'A',],
    'clear': [ 'C', 'B', 'A',],
    'holding': [],
    'armEmpty': True
    }
"""

startState = {
    'on': [],
    'onTable': ['A', 'B'],
    'clear': ['A', 'B'],
    'holding': [],
    'armEmpty': True
    }

goalState = {
    'on': [('B', 'A')],
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


def generateConjunct(preCondList, args):
    c = []
    for p in preCondList:
        t = []
        t.append(p[0])
        for a in p[1:]:
            #print a
            t.append(args[int(a[1])])
        t1 = tuple(t)
        c.append(tuple(['predicate', t1]))
    return tuple(['conjunct', c])


def generate_and_set_blocks_list(state):
    global blockList
    bList = set()
    on = state['on']
    for t in on:
        bList = bList.union(list(t))

    bList = bList.union(state['onTable'] + state['holding'] + state['clear'])
    blockList = list(bList)
    return bList

def plan_to_states_list(plan, start):
    out = []
    state = start
    s = conjunct_2_state(state)
    out.append(s)
    
    for action in plan:
        state = progress(state, action)
        s = conjunct_2_state(state)
        out.append(s)
        
    return out


def progress(state, action):
    # sanity checks have been assumed
    # ie the fact that the action _can_ be done is assumed by this function
    currentState = conjunct_2_state(state)
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
            currentState[d[0]] = False
        else:
            currentState[d[0]].remove(args[int(d[1][1])])
    
    return state_2_conjunct(currentState)        
    



# return only a _list_ of actions and no conjuncts
def get_actions_for_predicate(pred):
    
    p = pred[1]
    name = p[0]
    args = p[1:]
    actions = []
    if name == 'on':
        actions = [('action', ('stack', args[0], args[1]))]
    
    elif name == 'onTable':
        actions = [('action', ('putDown', args[0]))]
    
    elif name == 'clear':
        
        for b in blockList:
            if b != args[0]:
                actions.append(('action', ('stack', args[0], b)))
        for b in blockList:
            if b != args[0]:
                actions.append(('action', ('unStack', b, args[0])))

    elif name == 'holding':        

        actions.append(('action', ('pickup', args[0])))
        for b in blockList:
            if b != args[0]:
                actions.append(('action', ('unStack', args[0], b)))

    elif name == 'armEmpty':     

        for b in blockList:
            actions.append(('action', ('putDown', b)))
                
        for b1 in blockList:
            for b2 in blockList:
                if b1 != b2:
                    actions.append(('action', ('stack', b1, b2)))
        

    return actions


def isInState(pred, state):
    return pred in state[1]
    p = pred[1]
    name = p[0]
    if name == 'on':
        return p[1:] in state[name]
    elif name == 'armEmpty':
        return state[name]
    else:
        return p[1:] in state[name]



def check_all_solved(predList, state):
    allSolved = True
    for p in predList:
        if not isInState(p, state):
            allSolved = False
            break
    return allSolved

# convert from state dict to a conjuct form
def state_2_conjunct(state):
    conjunct = []
    
    if state['onTable']:
        for t in state['onTable']:
            p = ['predicate',]
            o = ['onTable',]
            o.append(t)
            p.append(tuple(o))
            conjunct.append(tuple(p))
                    
    if state['clear']:
        for t in state['clear']:
            p = ['predicate',]
            o = ['clear',]
            o.append(t)
            p.append(tuple(o))
            conjunct.append(tuple(p))
        
    if state['holding']:
        for t in state['holding']:
            p = ['predicate',]
            o = ['holding',]
            o.append(t)
            p.append(tuple(o))
            conjunct.append(tuple(p))
        
    if state['armEmpty']:
        p = ['predicate',]
        o = ['armEmpty',]
        p.append(tuple(o))
        conjunct.append(tuple(p))
        
    
    if state['on']:
        for t in state['on']:
            p = ['predicate',]
            o = ['on',]
            o.extend(t)
            p.append(tuple(o))
            conjunct.append(tuple(p))
    
    return tuple(['conjunct', conjunct])

def conjunct_2_state(conjunct):
    state = {
        'on' : [],
        'onTable' : [],
        'clear' : [],
        'holding' : [],
        'armEmpty' : False
        }
    for c in conjunct[1]:
        a = c[1]
        if a[0] == 'on':
            state['on'].append(a[1:])
        elif a[0] == 'onTable':
            state['onTable'].append(a[1])
        elif a[0] == 'clear':
            state['clear'].append(a[1])
        elif a[0] == 'holding':
            state['holding'].append(a[1])
        elif a[0] == 'armEmpty':
            state['armEmpty'] = True
    return state

def gsp_recursive(state, goal, openList): # return plan, new-state
    global counter
    plan = []
    g_type = goal[0]

    print counter,'#>>>>>>>>>>>>>\n'
    counter += 1
    print goal
    #print state
    if g_type == 'conjunct':
        predList = goal[1]
        ## print predList
        if not check_all_solved(predList, state):
            plan1, state1 = [], state    
            for p in predList:
                ## print p
                g = gsp_recursive(state1, p, openList)
                if g:
                    plan1, state1 = g
                    plan.extend(plan1)
                else: 

                   # # print goal
                    counter -= 1
                    print counter, '*<<<<<<<<<<<<<\n'
                    
                    return False

            if not check_all_solved(predList, state1):
                change = True
                while change:
                    for p in predList:
                        if not isInState(p, state1):
                            g = gsp_recursive(state1, p, openList)
                            if g:
                                plan1, state1 = g
                            	plan.extend(plan1)
                            	break # changed, start over
                            else:
                                # we need a better way to handle this.
                                return False
                    else:
                        change = False
                # all solved, peace
            counter -= 1
            print counter, '*<<<<<<<<<<<<<\n'
                    
            return plan, state1

        else: # if all are already solved
            counter -= 1
            print counter, '*<<<<<<<<<<<<<\n'
                    
            return [], state

    else: # goal is a predicate
        if isInState(goal, state):
            counter -= 1
            print counter, '*<<<<<<<<<<<<<\n'
                    
            return [], state
        elif goal in openList:
            print 'cupped, rolling back', goal
            counter -= 1
            print counter, '*<<<<<<<<<<<<<\n'
                    
            return False
        else:
            openList.append(goal)
            actions = get_actions_for_predicate(goal)
            plan1, state1 = [], state

            for a in actions:
                ## print a
                ## print '^^' 
                """
                if a in openList:# meaning we're gonna go into an infi loop; pack & rollback
                    print a
                    print 'cupped, rolling back'
                    counter -= 1
                    print counter, '*<<<<<<<<<<<<<\n'
                    
                    return False
                """
                name = a[1][0]
                args = a[1][1:]
                precondList = actionStore[name]['P']
                conjunct = generateConjunct(precondList, args)

                print a
                print conjunct
                print "___________"
                g = gsp_recursive(state1, conjunct, openList)
                if g: 
                    plan1, state1 = g
                    plan1.append(a)
                    counter -= 1
                    print counter, '*<<<<<<<<<<<<<\n'
                    rr = plan1, progress(state1, a)

                    return rr
                else:
                    continue
            else:
                counter -= 1
                print counter, '*<<<<<<<<<<<<<\n'
                return False


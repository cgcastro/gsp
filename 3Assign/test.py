import gsp
import json
import sys

print json.dumps(gsp.ss)
sys.exit()

s, g = gsp.state_2_conjunct(gsp.ss), gsp.state_2_conjunct(gsp.gg)
plan, state = gsp.gsp_recursive(s, g, [])
state = gsp.conjunct_2_state(state)

print state

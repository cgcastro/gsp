import gsp
s, g = gsp.state_2_conjunct(gsp.ss), gsp.state_2_conjunct(gsp.gg)
gsp.gsp_recursive(s, g, [])

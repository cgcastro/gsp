import tornado.ioloop
import tornado.web
import json
import gsp

class MainHandler(tornado.web.RequestHandler):
    def post(self, *args):
        inp = self.get_argument('data')
        dta = json.loads(inp)
        start = dta['start']
        goal = dta['goal']
        s = gsp.state_2_conjuct(start)
        g = gsp.state_2_conjuct(goal)
        state, plan = gsp.gsp_recursive(s, g, [])
        
        self.write("Hello, world")

application = tornado.web.Application([
    (r"/", MainHandler),
])

if __name__ == "__main__":
    application.listen(8888)
    tornado.ioloop.IOLoop.instance().start()


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

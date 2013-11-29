import tornado.ioloop
import tornado.web
import json
import gsp

class MainHandler(tornado.web.RequestHandler):
    
    def set_default_headers(self):
        self.set_header("Access-Control-Allow-Origin", "null")

    def post(self, *args):
        #inp = self.get_argument('data')
        dta = json.loads(self.request.body)
        start = dta['start']
        goal = dta['goal']
        s = gsp.state_2_conjunct(start)
        g = gsp.state_2_conjunct(goal)
        print "BLOCKSLIST", gsp.generate_and_set_blocks_list(start)
        #print gsp.blockList
        ps = gsp.gsp_recursive(s, g, [])
        states_list = None
        if ps:
            plan, state = ps
            states_list = gsp.plan_to_states_list(plan, s)
        else:
            states_list = []
        response = json.dumps(states_list)
        
        
        #self.write({"Response":"Done"})
        self.write(response)
        self.finish()


application = tornado.web.Application([
    (r"/", MainHandler),
])

if __name__ == "__main__":
    application.listen(4444)
    tornado.ioloop.IOLoop.instance().start()



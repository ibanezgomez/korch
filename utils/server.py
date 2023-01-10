from http.server import BaseHTTPRequestHandler,HTTPServer
from .daemon import Daemon
from .logger import log
import json
import ssl

class Server:

    def __init__(self, address='', port=8008, certfile=None, keyfile=None, ca_certs=None, auth_function=None, action_function=None):
        log.info(f"Starting API Server on port "+str(port))
        server_address = (address, port)

        #auth_function always returns {"success": True/False, "data" : AUTH_DATA } --> AUTH_DATA p.ej token decodificado, user/pwd, etc
        if action_function==None:
            action_function=self.defaultAuth

        srvHandler=ServerHandler(auth_function, action_function)

        httpd = HTTPServer(server_address, srvHandler)
        if certfile is not None and keyfile is not None and ca_certs is not None:
            httpd.socket = ssl.wrap_socket(httpd.socket, keyfile=keyfile, ca_certs=ca_certs, certfile=certfile, server_side=True)
        Daemon(httpd.serve_forever).start()

    def defaultAuth(self):
        AUTH_DATA={'usr': 'samuel'}
        return {"success": True/False, "data" : AUTH_DATA }


class ServerHandler(BaseHTTPRequestHandler):
    auth_function   = None
    action_function = None

    # This init is to set custom thins to the handler
    def __init__(self, auth_function=None, action_function=None):
        if auth_function==None: self.auth=self.authorized
        else: self.auth=auth_function
        if action_function!=None: self.action_function=action_function

    def _call_(self, *args, **kwargs):
        """ Handle a request """
        super()._init_(*args, **kwargs)

    def _set_headers(self):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()

    def do_HEAD(self):
        self._set_headers()

    # GET sends back a Hello world message
    def do_GET(self):
        self._set_headers()
        self.wfile.write(json.dumps({"success": True, "result": "I'm watching you"}).encode())

    # POST echoes the message adding a JSON field
    def do_POST(self):
        # refuse unauthorized content
        if 'Authorization' not in self.headers:
            self.send_response(401)
            self.end_headers()
            return
        else:
            auth=self.headers['Authorization']

        auth_result = self.auth(auth)

        # refuse unauthorized content
        if not auth_result["success"]:
            self.send_response(401)
            self.end_headers()
            return
        else:
            auth_data = auth_result["data"]

        # refuse to receive non-json content
        if 'Content-Type' not in self.headers or self.headers['Content-Type'] != 'application/json' or 'Content-Length' not in self.headers:
            self.send_response(400)
            self.end_headers()
            return
        else:
            ctype=self.headers['Content-Type']
            clength=int(self.headers['Content-Length'])

        if self.path == "/send":
            try:
                # read the data and convert it into a python dictionary
                input_data = json.loads(self.rfile.read(clength))
            except ValueError as e:
                self.send_response(400)
                self.end_headers()
                return
            
            if "action" not in input_data or "data" not in input_data:
                self.send_response(400)
                self.end_headers()
                return

            if self.action_function:
                if self.action_function(auth_data, input_data): response={"success": True, "result": "send triggered successful"}
                else: response={"success": False, "result": "send error"}
            else:
                print(input_data)
            # send the message back
            self._set_headers()
            self.wfile.write(json.dumps(response).encode())
            return True
        else:
            self.send_response(400)
            self.end_headers()
            return False

    def authorized(self, token):
        print("Checking auth for user %s" % (token))
        if token == "super_secret": return {"success" : True, "data" : "super_secret"}
        else: return {"success" : False, "data" : "KO"}
from http.server import BaseHTTPRequestHandler, HTTPServer
import json
import re

class HTTPRequestHandler(BaseHTTPRequestHandler):
    """HTTP request handler with additional properties and functions."""
    
    def do_GET(self):
        """handle GET requests."""
        reqs = {"/get_img", "/pearl1.jpg", "/pearl2.jpg"}
        req = self.path.split("&")
        req = req[0]
        print("REQUEST:", req)

        if not req in reqs:
            self._not_found()
        
        if req == "/get_img":
            self._set_response()
        if re.search(".\.jpg", req):
            self._send_img()

        print("GET request,\nPath: %s\nHeaders:\n%s\n", str(self.path), str(self.headers))
        # self._set_response()
        # self.wfile.write("GET request for {}".format(self.path).encode('utf-8'))

    def _set_response(self):
        self.send_response(200)
        self.send_header('Content-type', 'json')
        self.send_header('Access-Control-Allow-Origin', '*')  # Allow requests from any origin
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Origin, Content-Type')
        query = self.path
        q = [qc.split("=") for qc in query.split("&")]
        query_components = dict(qc.split("=") for qc in query.split("&")[1:])
        print("##############", query_components)


        self.end_headers()
        res = {"name": "pearl", "description": "pearl image", "url": f"/pearl{query_components['id']}.jpg"}
        res = json.dumps(res)
        self.wfile.write(f"{res}".encode())

    def _send_img(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        with open("./server_imgs" + self.path, 'rb') as content:
            self.wfile.write(content.read()) 

    
    def _not_found(self):
        self.send_response(401)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(f"401 Error, Page {self.path} not found".encode())

    def do_POST(self):
        content_length = int(self.headers['Content-Length']) # <--- Gets the size of data
        post_data = self.rfile.read(content_length) # <--- Gets the data itself
        print("POST request,\nPath: %s\nHeaders:\n%s\n\nBody:\n%s\n", str(self.path), str(self.headers), post_data.decode('utf-8'))

        self._set_response()
        self.wfile.write("POST request for {}".format(self.path).encode('utf-8'))


def run(server_class=HTTPServer, handler_class=HTTPRequestHandler):
    port = 8080
    server_address = ('127.0.0.1', port)
    httpd = server_class(server_address, handler_class)
    print(f"running on port {port}")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    httpd.server_close()

run()


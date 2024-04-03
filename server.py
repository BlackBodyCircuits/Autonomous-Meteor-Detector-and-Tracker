from http.server import BaseHTTPRequestHandler, HTTPServer
import json
import pprint
import re
import os

class HTTPRequestHandler(BaseHTTPRequestHandler):
    """HTTP request handler with additional properties and functions."""
    
    def do_GET(self):
        """handle GET requests."""

        req = self.path.split("&")
        req = req[0]
        print("REQUEST:", req)
        
        if req == "/get_img":
            self._set_response()
        elif re.search(".\.jpg", req):
            self._send_img()
        elif re.search(".\.txt", req):
            self._send_log()
        else:
            self._not_found()

        print("GET request,\nPath: %s\nHeaders:\n%s\n", str(req), str(self.headers))


    def _set_response(self):
        self.send_response(200)
        self._set_header()

        query = self.path
        q = [qc.split("=") for qc in query.split("&")]
        query_components = dict(qc.split("=") for qc in query.split("&")[1:])
        _, _, imgs = next(os.walk("./server_imgs"))
        print(len(imgs))
        query_components['id'] = int(query_components['id']) % len(imgs)
        print("##############", query_components)
        name = imgs[query_components['id']].removesuffix(".jpg")

        with open(f"./server_metadata/{name}.txt") as f:
            metadata = json.load(f)
            cam = metadata["camera"]
            date = metadata["date"]
            loc = metadata["location"]
        
        with open(f"./server_logs/{cam}.txt") as f:
            log_data = json.load(f)
        print("#################", log_data)



        res = {
                "name": f"{name}", 
               "camera": cam, 
               "date": date, 
               "loc": loc, 
               "img_url": f"/{name}.jpg", 
               "log_url": f"/{cam}.txt"
            #    "log_url": log_data
               }
        res = json.dumps(res)
        self.wfile.write(f"{res}".encode())

    def _send_img(self):
        self.send_response(200)
        self._set_header(content_type="text/html")
        with open("./server_imgs" + self.path, 'rb') as content:
            self.wfile.write(content.read()) 

    def _send_log(self):
        self.send_response(200)
        self._set_header(content_type="text/html")
        with open("./server_logs" + self.path, 'rb') as content:
            log_data = json.load(content)
            pretty_json_str = pprint.pformat(log_data)
            rem = {"{": "\n", "}": "", "'": ""}
            for char in rem.keys():
                pretty_json_str = pretty_json_str.replace(char, rem[char])

            print(pretty_json_str)
            self.wfile.write(pretty_json_str.encode('utf-8'))
            
    def _not_found(self):
        self.send_response(401)
        self._set_header(content_type="text/html")
        self.wfile.write(f"401 Error, Page {self.path} not found".encode())

    def _set_header(self, content_type="json"):
        self.send_header('Content-type', content_type)
        self.send_header('Access-Control-Allow-Origin', '*')  # Allow requests from any origin
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Origin, Content-Type')
        self.end_headers()

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


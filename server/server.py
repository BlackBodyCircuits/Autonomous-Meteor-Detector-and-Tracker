from http.server import BaseHTTPRequestHandler, HTTPServer
import json
import pprint
import re
import os
from detection_script import check_for_new_imgs, init_detection
import time

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
        elif req == "/load_imgs":
            self._load_imgs()
        else:
            self._not_found()

        print("GET request,\nPath: %s\nHeaders:\n%s\n", str(req), str(self.headers))


    def _set_response(self):
        self.send_response(200)
        self._set_header()

        query = self.path
        query_components = dict(qc.split("=") for qc in query.split("&")[1:])
        _, _, imgs = next(os.walk("./server_detections"))
        print(len(imgs))
        query_components['id'] = int(query_components['id']) % len(imgs)
        try:
            name = imgs[query_components['id']].removesuffix(".jpg")
        except AttributeError:
            name = imgs[query_components['id']][:-4]

        with open(f"./server_metadata/{name}_meta.json") as f:
            metadata = json.load(f)
            cam = metadata["Camera"]
            date = metadata["date"]
            loc = metadata["location"]

        res = {
                "name": f"{name}", 
               "camera": cam, 
               "date": date, 
               "loc": loc, 
               "img_url": f"/{name}.jpg", 
               "log_url": f"/{cam}.txt"
               }
        res = json.dumps(res)
        self.wfile.write(f"{res}".encode())

    def _send_img(self):
        self.send_response(200)

        query = self.path
        query_components = dict(qc.split("=") for qc in query.split("&")[1:])
        

        dir = "./server_detections"
        try:
            if query_components["raw"]:
                dir = "./server_imgs"
        except KeyError:
            pass
        
        self._set_header(content_type="text/html")
        with open(dir + self.path.split("&")[0], 'rb') as content:
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

    def _load_imgs(self):
        self.send_response(200)
        self._set_header()

        query = self.path
        q = [qc.split("=") for qc in query.split("&")]
        query_components = dict(qc.split("=") for qc in query.split("&")[1:])
        _, _, imgs = next(os.walk("./server_imgs"))
        imgs = sorted(imgs)
        print(len(imgs))
        print(query_components)

        prev_loaded = int(query_components["loaded_imgs"])
        num_to_load = int(query_components["load"])
        num_imgs = len(imgs)

        res_imgs = []

        if prev_loaded < num_imgs:
            max_load = prev_loaded + num_to_load
            if max_load >= num_imgs:
                max_load = num_imgs
            for i in range(prev_loaded, max_load):
                img_name = f"/{imgs[i]}"
                res_imgs.append(img_name)

        print(res_imgs)

        res = {"imgs": res_imgs}
        print(res)
        res = json.dumps(res)
        self.wfile.write(f"{res}".encode())
      
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

class custom_HTTPServer(HTTPServer):
    def __init__(self, server_address, handler_class) -> None:
        super().__init__(server_address, handler_class)
        self.last_check = time.time()
        self.seen_imgs = init_detection()

    def service_actions(self):
        if (time.time() - self.last_check) > 30:
            check_for_new_imgs(self.seen_imgs)
            self.last_check = time.time()
            print("RUNNING INFRENCE")


def run(server_class=custom_HTTPServer, handler_class=HTTPRequestHandler):
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


from http.server import BaseHTTPRequestHandler, HTTPServer
import json
import pprint
import re
import os
from detection_script import check_for_new_imgs, init_detection
import time
from datetime import datetime, timezone
import base64


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
        elif req == "/get_status":
            self._get_status()
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
        query_components['id'] = abs(int(query_components['id'])) % len(imgs)
        try:
            name = imgs[query_components['id']].removesuffix(".jpg")
        except AttributeError:
            name = imgs[query_components['id']][:-4]

        with open(f"./server_metadata/{name}_meta.json") as f:
            metadata = json.load(f)
            cam = metadata["Camera"]
            date = metadata["date"]
            loc = metadata["location"]
        
        log_txt = self.load_log_file(f"/{cam}.txt")

        res = {
                "name": f"{name}", 
               "camera": cam, 
               "date": date, 
               "loc": loc, 
               "img_url": f"/{name}.jpg", 
               "log_url": log_txt
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
                print("HERE####################")
                dir = "./server_imgs"
        except KeyError:
            pass

        print(dir)
        
        self._set_header(content_type="text/html")
        with open(dir + self.path.split("&")[0], 'rb') as content:
            self.wfile.write(content.read()) 

    def _send_log(self):
        self.send_response(200)
        self._set_header(content_type="text/html")
        log_txt = self.load_log_file(self.path)

        self.wfile.write(log_txt.encode('utf-8'))

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
      
    def _get_status(self):
        self.send_response(200)
        self._set_header()
        print("#################HERE")

        now = datetime.now(timezone.utc).replace(tzinfo=None)
        query = self.path
        #      "cams": {"ID": {"errs": [err_code], "time": [UTC_string], "connection": str}}
        res = {"cams": {}}

        for (root,dirs,files) in os.walk('./server_logs', topdown=True):
            
            for file in files:
                with open(os.path.join(root, file), 'r') as content:
                    log_data = json.load(content)
                    ID = int(file.split(".")[0])
                    data = {"errs": [], "time": [], "connection": "CONNECTED"}

                    last_date = list(log_data.keys())[-1]
                    last_date_time = datetime.strptime(last_date,'%Y-%m-%dT%H:%M:%SZ')
                    if (now  - last_date_time).total_seconds() > 20 * 60:
                        data["connection"] = "DISCONNECTED"

                    for date in log_data.keys():
                        log = log_data[date]
                        print(log, ID)
                        if log["status"] != "GOOD":
                            data["errs"].append(log["status"])
                            data["time"].append(date)

                    res["cams"][ID] = data
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

    def load_log_file(self, fname):
        with open("./server_logs" + fname, 'rb') as content:
            log_data = json.load(content)
            pretty_json_str = pprint.pformat(log_data)[1:-1]
            rem = {"{": "\n&&", "}": "$$", "'": ""}
            for char in rem.keys():
                pretty_json_str = pretty_json_str.replace(char, rem[char])

            print(pretty_json_str)
        return pretty_json_str


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


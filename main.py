import mimetypes
import json
import urllib.parse
import socket
from threading import RLock, Thread
from http.server import HTTPServer, BaseHTTPRequestHandler
from datetime import datetime
from pathlib import Path

storage_path = Path("storage")
storage_path.mkdir(parents=True, exist_ok=True)

server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_address = ("", 5000)
server_socket.bind(server_address)

lock = RLock()

def save_message_to_json(data_dict):
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")
    data = {current_time: data_dict}

    file_path = storage_path / "data.json"
    with lock:
        if file_path.exists():
            with open(file_path, "r") as file:
                try:
                    existing_data = json.load(file)
                    # existing_data.append("\n")
                    print(existing_data)
                except json.JSONDecodeError:
                    existing_data = []
        else:
            existing_data = []

        existing_data.append(data)
        print(existing_data)

        with open(file_path, "w") as file:
            json.dump(existing_data, file, indent=4)

class HttpHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        pr_url = urllib.parse.urlparse(self.path)
        if pr_url.path == '/':
            self.send_html_file('index.html')
        elif pr_url.path == '/message':
            self.send_html_file('message.html')
        else:
            if Path().joinpath(pr_url.path[1:]).exists():
                self.send_static()
            else:
                self.send_html_file('error.html', 404)

    def send_html_file(self, filename, status=200):
        self.send_response(status)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        with open(filename, 'rb') as fd:
            self.wfile.write(fd.read())

    def send_static(self):
        self.send_response(200)
        mt = mimetypes.guess_type(self.path)
        if mt:
            self.send_header("Content-type", mt[0])
        else:
            self.send_header("Content-type", 'text/plain')
        self.end_headers()
        with open(f'.{self.path}', 'rb') as file:
            self.wfile.write(file.read())

    def _set_response(self):
        self.send_response(302)
        self.send_header('Location', '/')
        self.end_headers()

    def do_POST(self):
        data = self.rfile.read(int(self.headers['Content-Length']))
        print(data)
        data_parse = urllib.parse.unquote_plus(data.decode())
        print(data_parse)
        data_dict = {key: value for key, value in [el.split('=') for el in data_parse.split('&')]}
        # print(data_dict)
        try:
            send_message_via_socket(json.dumps(data_dict))
            self._set_response()
            self.wfile.write(b"Message received and saved successfully!")
        except json.JSONDecodeError:
            self._set_response()
            self.wfile.write(b"Error: Invalid data format.")
        # self.send_response(302)
        # self.send_header('Location', '/')
        # self.end_headers()


def run_http_server(server_class=HTTPServer, handler_class=HttpHandler):
    server_address = ('', 3000)
    http = server_class(server_address, handler_class)
    try:
        http.serve_forever()
    except KeyboardInterrupt:
        http.server_close()

def send_message_via_socket(data):
    server_socket.sendto(data.encode(), ("localhost", 5000))

def run_socket_server():
    while True:
        data, address = server_socket.recvfrom(4096)
        try:
            data_dict = json.loads(data.decode())
        except json.JSONDecodeError:
            print("Error: Incorrect type of data.")
            continue

        save_message_to_json(data_dict)

        print("Data save in file data.json.")


if __name__ == '__main__':
    http_thread = Thread(target=run_http_server)
    http_thread.start()

    socket_thread = Thread(target=run_socket_server)
    socket_thread.start()

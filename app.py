from http.server import HTTPServer, BaseHTTPRequestHandler
import urllib.parse
import mimetypes
import pathlib
from datetime import datetime
import json
import os
from jinja2 import FileSystemLoader, Environment


class HttpHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        pr_url = urllib.parse.urlparse(self.path)
        if pr_url.path == "/":
            self.send_html_file("index.html")
        elif pr_url.path == "/message":
            self.send_html_file("contact.html")
        elif pr_url.path == "/read":
            env = Environment(loader=FileSystemLoader("."))

            template = env.get_template("read.html")
            file_path = "storage/data.json"
            with open(file_path, "r", encoding="utf-8") as file:
                storage = json.load(file)

            rendered = template.render(messages=storage)

            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.wfile.write(rendered.encode("utf-8"))

        else:
            if pathlib.Path().joinpath(pr_url.path[1:]).exists():
                self.send_static()
            else:
                self.send_html_file("error.html", 404)

    def send_html_file(self, filename, status=200):
        self.send_response(status)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        with open(filename, "rb") as fd:
            self.wfile.write(fd.read())

    def send_static(self):
        self.send_response(200)
        mt = mimetypes.guess_type(self.path)
        if mt:
            self.send_header("Content-type", mt[0])
        else:
            self.send_header("Content-type", "text/plain")
        self.end_headers()
        with open(f".{self.path}", "rb") as file:
            self.wfile.write(file.read())

    def save_form(self, new_data):
        file_path = "storage/data.json"
        try:
            if os.path.exists(file_path):
                with open(file_path, "r", encoding="utf-8") as file:
                    storage = json.load(file)
            else:
                storage = {}

            storage[datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")] = new_data

            with open(file_path, "w", encoding="utf-8") as file:
                json.dump(storage, file, ensure_ascii=False, indent=4)

        except Exception as e:
            print(f"Error: {e}")

    def do_POST(self):
        data = self.rfile.read(int(self.headers["Content-Length"]))
        print(data)
        data_parse = urllib.parse.unquote_plus(data.decode())
        print(data_parse)
        data_dict = {
            key: value for key, value in [el.split("=") for el in data_parse.split("&")]
        }

        self.save_form(data_dict)
        self.send_response(302)
        self.send_header("Location", "/")
        self.end_headers()


def run(server_class=HTTPServer, handler_class=HttpHandler):
    server_address = ("", 3000)
    http = server_class(server_address, handler_class)
    try:
        http.serve_forever()
    except KeyboardInterrupt:
        http.server_close()


if __name__ == "__main__":
    run()

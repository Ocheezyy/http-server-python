from app.routes import RouteMethodRes, file_route, echo_route, user_agent_route, index_route
import gzip
import threading
import socket
import os
import re
import sys


PATH_REGEX = r".+?(?=\/)"
CRLF = "\r\n"
AVAILABLE_PATHS: list[str] = ["/", "/echo", "/user-agent"]
PORT: int = 4221
HOST: str = "localhost"
DIRECTORY: str = sys.argv[2] if len(sys.argv) > 2 else ""
ACCEPTED_ENCODING_TYPES: list[str] = ["gzip"]

print(DIRECTORY)


def send_response(sock: socket.socket, res_msg: str) -> None:
    sock.send(bytes(res_msg, "utf-8"))

def send_500(sock: socket.socket, http_ver: str) -> None:
    send_response(sock, f"{http_ver} 500 Internal Server Error{CRLF}{CRLF}")

def send_404(sock: socket.socket, http_ver: str) -> None:
    send_response(sock, f"{http_ver} 404 Not Found{CRLF}{CRLF}")

def build_response(res_obj: RouteMethodRes, http_ver: str, encoding: str) -> str:
    res_str = f"{http_ver} {res_obj['status']} {res_obj['msg']}{CRLF}"
    if len(res_obj["headers"]) != 0:
        if encoding != "":
            new_headers = list(filter(lambda x: "Content-Length" not in x, res_obj["headers"]))
            res_str += CRLF.join(new_headers)
        else:
            res_str += CRLF.join(res_obj["headers"])

    if encoding != "":
        res_str += f"{CRLF}Content-Encoding: {encoding}"
        if encoding == "gzip":
            encoded_body = gzip.compress(f"{CRLF}{CRLF}{res_obj['body']}".encode())
            # TODO: Content-length not working correctly
            res_str += f"{CRLF}Content-Length: {len(encoded_body)}"
            res_str += f"{CRLF}{CRLF}{encoded_body}"
        else:
            res_str += f"{CRLF}{CRLF}{res_obj['body']}"
    else:
        res_str += f"{CRLF}{CRLF}{res_obj['body']}"

    return res_str


def handle_encoding(headers: dict) -> str:
    encoding_type: str = ""
    if "accept-encoding" in headers:
        encoding_header = headers["accept-encoding"]
        if ", " in encoding_header:
            possible_encodings = encoding_header.split(", ")
            for encoding in possible_encodings:
                if encoding in ACCEPTED_ENCODING_TYPES:
                    encoding_type = encoding
        else:
            encoding_type = encoding_header
        if encoding_type not in ACCEPTED_ENCODING_TYPES:
            encoding_type = ""
    return encoding_type


def read_headers(list_headers: list[str]) -> dict:
    header_obj: dict = {}
    for header in list_headers:
        key, value = header.split(": ")
        header_obj[key.lower()] = value

    print(header_obj)
    return header_obj


def base_req_handler(req_sock: socket.socket, req_address) -> None:
    req_bytes: bytes = req_sock.recv(1024)
    req: str = req_bytes.decode()
    req_lines: list[str] = req.splitlines()
    req_lines.pop() if req_lines[-1] == "" else req_lines.pop(-2) # Could be problematic
    req_verb, req_path, req_http_ver = req_lines[0].split(" ")
    req_lines.pop(0) # Removes verb and version

    req_headers = read_headers(req_lines)

    print(f"request path: {req_path}")
    res_obj: RouteMethodRes
    if req_path == "/":
        res_obj = index_route()
    elif req_path.startswith("/echo"):
        res_obj = echo_route(req_path)
    elif req_path.startswith("/user-agent"):
        res_obj = user_agent_route(req_headers)
    elif req_path.startswith("/files"):
        res_obj = file_route(req_path, req_verb, req_lines[-1], DIRECTORY)
    else:
        send_404(req_sock, req_http_ver)
        return


    encoding_type: str = handle_encoding(req_headers)

    res_str = build_response(res_obj, req_http_ver, encoding_type)
    send_response(req_sock, res_str)


def main():
    server_socket = socket.create_server((HOST, PORT), reuse_port=True)
    while True:
        req_sock, req_addr = server_socket.accept() # wait for client
        threading.Thread(target=base_req_handler, args=(req_sock, req_addr)).start()


if __name__ == "__main__":
    main()

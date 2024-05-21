# Uncomment this to pass the first stage
from typing import TypedDict
import socket
import re



class RouteMethodRes(TypedDict):
    status: int
    msg: str
    body: str
    headers: list[str]

def index_route() -> RouteMethodRes:
    return {
        "status": 200,
        "msg": "OK",
        "body": "",
        "headers": []
    }

def echo_route(full_req_path: str) -> RouteMethodRes:
    echo_str: str = full_req_path.replace("/echo/", "")
    return {
        "status": 200,
        "msg": "OK",
        "body": echo_str,
        "headers": ["Content-Type: text/plain", f"Content-Length: {len(echo_str)}"]
    }


def send_response(sock: socket.socket, res_msg: str) -> None:
    sock.send(bytes(res_msg, "utf-8"))

def send_500(sock: socket.socket, http_ver: str) -> None:
    send_response(sock, f"{http_ver} 500 Internal Server Error\r\n\r\n")

def send_404(sock: socket.socket, http_ver: str) -> None:
    send_response(sock, f"{http_ver} 404 Not Found\r\n\r\n")

def build_response(res_obj: RouteMethodRes, http_ver: str) -> str:
    res_str = f"{http_ver} {res_obj['status']} {res_obj['msg']}\r\n"
    if len(res_obj["headers"]) != 0:
        res_str += "\r\n".join(res_obj["headers"])

    res_str += f"\r\n\r\n{res_obj['body']}"
    return res_str


def main():
    PATH_REGEX = r".+?(?=\/)"
    AVAILABLE_PATHS: list[str] = ["/", "/echo"]
    # Look into this methods logic to allow for a one line call of any path
    PATH_METHODS: dict[str, function] = {
        "/": index_route,
        "/echo": echo_route
    }
    PORT: int = 4221
    HOST: str = "localhost"
    # You can use print statements as follows for debugging, they'll be visible when running tests.
    print("Logs from your program will appear here!")

    server_socket = socket.create_server((HOST, PORT), reuse_port=True)
    req_sock, req_addr = server_socket.accept() # wait for client
    req_bytes: bytes = req_sock.recv(1024)
    req: str = req_bytes.decode()
    req_lines: list[str] = req.splitlines()
    req_lines.pop() # Remove empty space
    req_verb, req_path, req_http_ver = req_lines[0].split(" ")
    req_lines.pop(0) # Removes verb and version
    # Need to add header handling here

    print(f"request path: {req_path}")
    res_obj: RouteMethodRes
    if req_path == "/":
        res_obj = index_route()
    elif req_path.startswith("/echo"):
        res_obj = echo_route(req_path)
    else:
        send_404(req_sock, req_http_ver)
        return

    # if req_path != "/":
    #     re_req = re.search(PATH_REGEX, req_path)
    #     if not re_req:
    #         print("Regex on path failed")
    #         send_500(req_sock, req_http_ver)
    #         return
    #     req_base_path = re_req.group(0)
    #     if req_base_path not in AVAILABLE_PATHS:
    #         print("Path not recognized")
    #         send_404(req_sock, req_http_ver)
    #         return
    #     match req_base_path:
    #         case "/echo":
    #             res_obj = echo_route(req_path)
    #         case _:
    #             print("Default match statement reached")
    #             send_500(req_sock, req_http_ver)
    #             return

    res_str = build_response(res_obj, req_http_ver)
    send_response(req_sock, res_str)


if __name__ == "__main__":
    main()

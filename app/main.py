# Uncomment this to pass the first stage
import socket


def main():
    AVAILABLE_PATHS: list[str] = ["/"]
    # You can use print statements as follows for debugging, they'll be visible when running tests.
    print("Logs from your program will appear here!")

    # Uncomment this to pass the first stage
    #
    PORT: int = 4221
    HOST: str = "localhost"
    server_socket = socket.create_server((HOST, PORT), reuse_port=True)
    req_sock, req_addr = server_socket.accept() # wait for client
    req_bytes: bytes = req_sock.recv(1024)
    req: str = req_bytes.decode()
    req_lines: list[str] = req.splitlines()
    req_lines.pop() # Remove empty space
    req_verb, req_path, req_http_ver = req_lines[0].split(" ")

    req_status = 200
    req_msg = "OK"
    if req_path not in AVAILABLE_PATHS:
        req_status = 404
        req_msg = "Not Found"

    req_lines.pop(0)
    # print(req_lines)
    res_line: str = f"{req_http_ver} {req_status} {req_msg}\r\n\r\n"

    req_sock.send(bytes(res_line, "utf-8"))


if __name__ == "__main__":
    main()

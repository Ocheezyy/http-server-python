from typing import LiteralString, TypedDict
import os

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

def user_agent_route(headers: dict) -> RouteMethodRes:
    user_agent_header: str = headers["user-agent"]
    user_agent: str = user_agent_header.split(": ")[1].rstrip("\r\n")
    return {
        "status": 200,
        "msg": "OK",
        "body": user_agent,
        "headers": ["Content-Type: text/plain", f"Content-Length: {len(user_agent)}"]
    }

def file_route(full_req_path: str, http_verb: str, req_body: str, files_dir: str) -> RouteMethodRes:
    file_name = full_req_path.replace("/files/", "")
    file_path = os.path.join(files_dir, file_name)
    if http_verb == "GET":
        if not os.path.exists(file_path):
            return {
                "status": 404,
                "msg": "Not Found",
                "body": "",
                "headers": []
            }

        with open (file_path, "r") as reader:
            contents = reader.read()

        return {
            "status": 200,
            "msg": "OK",
            "body": contents,
            "headers": ["Content-Type: application/octet-stream", f"Content-Length: {len(contents)}"]
        }
    elif http_verb == "POST":
        with open (file_path, "w") as writer:
            writer.write(req_body)

        return {
            "status": 201,
            "msg": "Created",
            "body": "",
            "headers": []
        }
    else:
        return {
            "status": 405,
            "msg": "Method Not Allowed",
            "body": "",
            "headers": []
        }

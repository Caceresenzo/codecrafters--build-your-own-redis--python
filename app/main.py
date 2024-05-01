import os
import sys
import socket

STATUS_PHRASES = {
    200: "OK",
    404: "Not Found"
}


def main():
    print("codecrafters build-your-own-http")

    server = socket.create_server(("0.0.0.0", 4221), reuse_port=True)
    while True:
        client, addr = server.accept()

        print("connected", addr)

        pid = os.fork()
        if pid:
            continue

        io = socket.SocketIO(client, "rw")

        request_line = io.readline()[:-2].decode("ascii")
        parts = request_line.split(" ")
        method, path, version = parts

        headers = {}
        while line := io.readline()[:-2].decode("ascii"):
            key, value = line.split(": ")
            headers[key.lower()] = value

        if path == "/":
            response = 200, {}, None
        elif path.startswith("/echo/"):
            message = path[6:]

            response = (
                200,
                {
                    "Content-Type": "text/plain",
                    "Content-Length": str(len(message)),
                },
                message.encode("ascii")
            )
        elif path == "/user-agent":
            message = headers["User-Agent".lower()]

            response = (
                200,
                {
                    "Content-Type": "text/plain",
                    "Content-Length": str(len(message)),
                },
                message.encode("ascii")
            )
        else:
            response = 404, {}, None

        status, headers, body = response
        phrase = STATUS_PHRASES[status]

        client.send(f"HTTP/1.1 {status} {phrase}\r\n".encode("ascii"))
        for key, value in headers.items():
            client.send(f"{key}: {value}\r\n".encode("ascii"))
        client.send(b"\r\n")

        if body is not None:
            client.send(body)

        client.close()
        exit(0)


if __name__ == "__main__":
    main()

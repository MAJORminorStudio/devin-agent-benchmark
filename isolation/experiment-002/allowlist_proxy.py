"""Minimal CONNECT proxy for the disposable Experiment 002 network.

The proxy deliberately permits only the Devin service hosts. It is a tunnel
proxy, so HTTPS payloads remain opaque to the proxy and the Devin container
cannot reach the external network without passing this host allowlist.
"""

from __future__ import annotations

import select
import socket
import socketserver


ALLOWED_HOSTS = frozenset(
    {
        "api.devin.ai",
        "app.devin.ai",
        "server.codeium.com",
    }
)


class ProxyHandler(socketserver.StreamRequestHandler):
    def handle(self) -> None:
        line = self.rfile.readline(8192)
        if not line:
            return
        parts = line.decode("latin1", errors="replace").strip().split()
        if len(parts) != 3 or parts[0].upper() != "CONNECT":
            self.wfile.write(b"HTTP/1.1 405 Method Not Allowed\r\n\r\n")
            return
        host, separator, port_text = parts[1].rpartition(":")
        if not separator or host.lower().rstrip(".") not in ALLOWED_HOSTS:
            self.wfile.write(b"HTTP/1.1 403 Forbidden\r\n\r\n")
            return
        try:
            port = int(port_text)
            if port != 443:
                raise ValueError("only HTTPS CONNECT is allowed")
            upstream = socket.create_connection((host, port), timeout=15)
        except (OSError, ValueError):
            self.wfile.write(b"HTTP/1.1 502 Bad Gateway\r\n\r\n")
            return
        with upstream:
            self.wfile.write(b"HTTP/1.1 200 Connection Established\r\n\r\n")
            self._relay(self.connection, upstream)

    @staticmethod
    def _relay(left: socket.socket, right: socket.socket) -> None:
        while True:
            readable, _, exceptional = select.select([left, right], [], [left, right], 60)
            if exceptional or not readable:
                return
            for source in readable:
                data = source.recv(65536)
                if not data:
                    return
                destination = right if source is left else left
                destination.sendall(data)


class ThreadingProxy(socketserver.ThreadingMixIn, socketserver.TCPServer):
    allow_reuse_address = True
    daemon_threads = True


if __name__ == "__main__":
    with ThreadingProxy(("0.0.0.0", 3128), ProxyHandler) as server:
        server.serve_forever()

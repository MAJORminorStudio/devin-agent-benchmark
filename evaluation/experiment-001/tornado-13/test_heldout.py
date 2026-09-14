"""Evaluator-only behavioral checks for Tornado 13."""

import socket

from tornado.http1connection import HTTP1Connection
from tornado.httputil import HTTPMessageDelegate
from tornado.iostream import IOStream
from tornado.locks import Event
from tornado.netutil import add_accept_handler
from tornado.testing import AsyncTestCase, bind_unused_port, gen_test


class HTTP10ResponseBehaviorTest(AsyncTestCase):
    def setUp(self):
        super(HTTP10ResponseBehaviorTest, self).setUp()
        self.asyncSetUp()

    @gen_test
    def asyncSetUp(self):
        listener, port = bind_unused_port()
        connected = Event()

        def accept_callback(connection, address):
            del address
            self.server_stream = IOStream(connection)
            self.addCleanup(self.server_stream.close)
            connected.set()

        add_accept_handler(listener, accept_callback)
        self.client_stream = IOStream(socket.socket())
        self.addCleanup(self.client_stream.close)
        yield [
            self.client_stream.connect(("127.0.0.1", port)),
            connected.wait(),
        ]
        self.io_loop.remove_handler(listener)
        listener.close()

    @gen_test
    def test_http10_bodyless_response_without_length_is_read(self):
        connection = HTTP1Connection(self.client_stream, True)
        self.server_stream.write(b"HTTP/1.0 204 No Content\r\n\r\n")
        self.server_stream.close()

        finished = Event()
        test = self

        class Delegate(HTTPMessageDelegate):
            def headers_received(self, start_line, headers):
                del headers
                test.status = start_line.code

            def data_received(self, data):
                test.body = getattr(test, "body", b"") + data

            def finish(self):
                finished.set()

        yield connection.read_response(Delegate())
        yield finished.wait()
        self.assertEqual(self.status, 204)
        self.assertEqual(getattr(self, "body", b""), b"")

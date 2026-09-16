"""Evaluator-only behavioral checks for Scrapy 3."""

from scrapy import Request, Spider
from scrapy.http import Response
from scrapy.settings import Settings

from scrapy.downloadermiddlewares.redirect import RedirectMiddleware


def test_protocol_relative_redirect_uses_request_scheme_and_host():
    settings = Settings({
        "REDIRECT_ENABLED": True,
        "REDIRECT_MAX_TIMES": 20,
        "REDIRECT_PRIORITY_ADJUST": 2,
    })
    middleware = RedirectMiddleware(settings)
    request = Request("https://origin.example.test/start", method="GET")
    response = Response(
        request.url,
        status=302,
        headers={"Location": "///cdn.example.test/next"},
    )

    redirected = middleware.process_response(request, response, Spider("heldout"))

    assert redirected is not response
    assert redirected.url == "https://cdn.example.test/next"
    assert redirected.method == "GET"

from starlette.responses import JSONResponse
from starlette.types import ASGIApp, Message, Receive, Scope, Send


class SecurityHeadersMiddleware:
    """Apply security headers to HTTP responses."""

    def __init__(self, app: ASGIApp) -> None:
        self.app = app

    async def __call__(
        self,
        scope: Scope,
        receive: Receive,
        send: Send,
    ) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        async def send_with_security_headers(message: Message) -> None:
            if message["type"] == "http.response.start":
                headers = list(message.get("headers", []))

                security_headers = [
                    (b"x-content-type-options", b"nosniff"),
                    (b"x-frame-options", b"DENY"),
                    (b"referrer-policy", b"no-referrer"),
                    (
                        b"permissions-policy",
                        b"camera=(), microphone=(), geolocation=()",
                    ),
                    (b"cache-control", b"no-store"),
                ]

                existing = {key.lower() for key, _ in headers}

                for name, value in security_headers:
                    if name not in existing:
                        headers.append((name, value))

                message = {**message, "headers": headers}

            await send(message)

        await self.app(scope, receive, send_with_security_headers)


class RequestSizeLimitMiddleware:
    """Reject HTTP request bodies exceeding the configured limit."""

    def __init__(
        self,
        app: ASGIApp,
        max_body_size: int = 16_384,
    ) -> None:
        self.app = app
        self.max_body_size = max_body_size

    async def __call__(
        self,
        scope: Scope,
        receive: Receive,
        send: Send,
    ) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        headers = dict(scope.get("headers", []))
        content_length = headers.get(b"content-length")

        if content_length is not None:
            try:
                declared_size = int(content_length)
            except ValueError:
                response = JSONResponse(
                    status_code=400,
                    content={"detail": "Invalid Content-Length header"},
                )
                await response(scope, receive, send)
                return

            if declared_size < 0:
                response = JSONResponse(
                    status_code=400,
                    content={"detail": "Invalid Content-Length header"},
                )
                await response(scope, receive, send)
                return

            if declared_size > self.max_body_size:
                response = JSONResponse(
                    status_code=413,
                    content={"detail": "Request body too large"},
                )
                await response(scope, receive, send)
                return

        received_size = 0

        async def limited_receive() -> Message:
            nonlocal received_size

            message = await receive()

            if message["type"] == "http.request":
                received_size += len(message.get("body", b""))

                if received_size > self.max_body_size:
                    raise RequestBodyTooLarge

            return message

        try:
            await self.app(scope, limited_receive, send)

        except RequestBodyTooLarge:
            response = JSONResponse(
                status_code=413,
                content={"detail": "Request body too large"},
            )
            await response(scope, receive, send)


class RequestBodyTooLarge(Exception):
    """Raised when an incoming request exceeds the body size limit."""

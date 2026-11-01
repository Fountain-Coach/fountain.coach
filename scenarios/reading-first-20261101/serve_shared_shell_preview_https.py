#!/usr/bin/env python3
"""HTTPS entrypoint for the existing source-locked owner-WLAN Fountain Press stage.

Uses the existing stage Handler and inspect contract. This is a second HTTPS
view of the *same* active release, not a second publication authority.
"""
from __future__ import annotations
import argparse
import pathlib
import re
import ssl
from functools import partial
from http.server import ThreadingHTTPServer
from urllib.parse import urlsplit
from serve_shared_shell_preview import Handler, inspect


class SecureStageHandler(Handler):
    """Preserve the existing stage routes, with HTTP byte ranges for MP3 takes."""

    def send_head(self):
        pathname = urlsplit(self.path).path
        if not (
            pathname.startswith("/estate/essays/the-door-is-a-score/media/")
            and pathname.lower().endswith(".mp3")
        ):
            return super().send_head()

        self._partial_bytes = None
        path = pathlib.Path(self.translate_path(self.path)).resolve()
        root = pathlib.Path(self.directory).resolve()
        if not path.is_relative_to(root) or not path.is_file():
            self.send_error(404, "Media unavailable")
            return None

        size = path.stat().st_size
        request_range = self.headers.get("Range")
        if self.headers.get("If-Range"):
            request_range = None
        start, end, status = 0, size - 1, 200
        if request_range:
            match = re.fullmatch(r"bytes=(\d*)-(\d*)", request_range.strip())
            if not match or not any(match.groups()) or not size:
                return self._range_unsatisfied(size)
            first, last = match.groups()
            if first:
                start = int(first)
                end = min(int(last), size - 1) if last else size - 1
            else:
                suffix = int(last)
                if not suffix:
                    return self._range_unsatisfied(size)
                start = max(0, size - suffix)
            if start >= size or end < start:
                return self._range_unsatisfied(size)
            status = 206

        source = path.open("rb")
        source.seek(start)
        self._partial_bytes = end - start + 1
        self.send_response(status)
        self.send_header("Content-Type", self.guess_type(str(path)))
        self.send_header("Content-Length", str(self._partial_bytes))
        self.send_header("Accept-Ranges", "bytes")
        self.send_header("Last-Modified", self.date_time_string(path.stat().st_mtime))
        if status == 206:
            self.send_header("Content-Range", f"bytes {start}-{end}/{size}")
        self.end_headers()
        return source

    def _range_unsatisfied(self, size):
        self.send_response(416)
        self.send_header("Content-Range", f"bytes */{size}")
        self.send_header("Content-Length", "0")
        self.send_header("Accept-Ranges", "bytes")
        self.end_headers()
        return None


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", required=True, type=pathlib.Path)
    parser.add_argument("--bind", default="192.168.8.50")
    parser.add_argument("--port", type=int, default=8243)
    parser.add_argument("--cert", required=True)
    parser.add_argument("--key", required=True)
    args = parser.parse_args()

    # Source-locked canonical staging is an explicit, checked-in projection.
    meta = inspect(args.root)
    landing = meta.get("personalWorksLanding")
    if landing is not None and not (
        isinstance(landing, dict)
        and landing.get("stageFrom") == "/pointer/"
        and landing.get("stageTo") == "/works/"
        and landing.get("httpStatus") == 308
        and landing.get("sourceOwner") == "Fountain-Coach/benedikt-eickhoff.de"
        and landing.get("stageOnly") is True
    ):
        raise RuntimeError("Invalid personal Works stage redirect")

    context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    context.minimum_version = ssl.TLSVersion.TLSv1_2
    context.load_cert_chain(args.cert, args.key)
    server = ThreadingHTTPServer(
        (args.bind, args.port),
        partial(
            SecureStageHandler,
            root=args.root.resolve(strict=True),
            personal_works_landing=landing is not None,
        ),
    )
    server.daemon_threads = True
    server.socket = context.wrap_socket(server.socket, server_side=True)
    print(f"READY Fountain Press secure WLAN stage {args.bind}:{args.port}", flush=True)
    server.serve_forever()


if __name__ == "__main__":
    main()

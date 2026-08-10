#!/usr/bin/env python3
"""Local preview server with no-cache headers (avoids stale HTML when switching menus)."""
from __future__ import annotations

import argparse
import functools
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path


class NoCacheHandler(SimpleHTTPRequestHandler):
    def end_headers(self) -> None:
        self.send_header("Cache-Control", "no-store, no-cache, must-revalidate, max-age=0")
        self.send_header("Pragma", "no-cache")
        self.send_header("Expires", "0")
        super().end_headers()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("-p", "--port", type=int, default=8080)
    parser.add_argument(
        "-d",
        "--directory",
        type=Path,
        default=Path(__file__).resolve().parent,
        help="Document root (default: this docs/ folder)",
    )
    args = parser.parse_args()
    root = args.directory.resolve()
    handler = functools.partial(NoCacheHandler, directory=str(root))
    server = ThreadingHTTPServer(("127.0.0.1", args.port), handler)
    print(f"Serving {root} at http://127.0.0.1:{args.port}/ (Cache-Control: no-store)")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopped.")


if __name__ == "__main__":
    main()

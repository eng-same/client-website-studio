#!/usr/bin/env python3
"""Serve a built preview folder on this computer only (127.0.0.1).

    serve_preview.py preview            -> http://127.0.0.1:8080/
    serve_preview.py preview --port 9000

Run it in the background after every preview build, without asking the marketer.
It never listens on the network, only on localhost. Stop it with Ctrl+C or by
ending the process.
"""
from __future__ import annotations

import argparse
import functools
import http.server
import socketserver
import sys
from pathlib import Path

sys.dont_write_bytecode = True


class Quiet(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *args):
        pass


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('folder', type=Path, help='the preview folder')
    parser.add_argument('--port', type=int, default=8080)
    args = parser.parse_args()
    folder = args.folder.resolve()
    if not (folder / 'index.html').is_file():
        parser.error('the folder must contain index.html')

    handler = functools.partial(Quiet, directory=str(folder))
    socketserver.TCPServer.allow_reuse_address = True
    for port in range(args.port, args.port + 20):
        try:
            server = socketserver.TCPServer(('127.0.0.1', port), handler)
            break
        except OSError:
            continue
    else:
        raise SystemExit('No free port found')
    print(f'Preview running: http://127.0.0.1:{port}/ar/index.html', flush=True)
    with server:
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            pass


if __name__ == '__main__':
    main()

from __future__ import annotations

import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from src.datacenter_roadmap_strategy_console.engine import load_json, prioritize_roadmap


ROOT = Path(__file__).resolve().parent
WEB_ROOT = ROOT / "web"


class Handler(BaseHTTPRequestHandler):
    def do_GET(self) -> None:  # noqa: N802
        if self.path == "/api/run":
            customers = load_json(ROOT / "samples" / "customers.json")
            technologies = load_json(ROOT / "samples" / "technologies.json")
            competitors = load_json(ROOT / "samples" / "competitors.json")
            self._send_json(prioritize_roadmap(customers, technologies, competitors))
            return
        target = "index.html" if self.path in ("/", "") else self.path.lstrip("/")
        file_path = WEB_ROOT / target
        if file_path.exists() and file_path.is_file():
            self._send_file(file_path)
            return
        self.send_error(404, "Not Found")

    def log_message(self, format: str, *args) -> None:  # noqa: A003
        return

    def _send_json(self, payload: dict) -> None:
        body = json.dumps(payload).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _send_file(self, path: Path) -> None:
        content_type = {
            ".html": "text/html; charset=utf-8",
            ".css": "text/css; charset=utf-8",
            ".js": "application/javascript; charset=utf-8",
        }.get(path.suffix, "application/octet-stream")
        body = path.read_bytes()
        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


def main() -> None:
    server = ThreadingHTTPServer(("127.0.0.1", 8003), Handler)
    print("Roadmap strategy dashboard running at http://127.0.0.1:8003")
    server.serve_forever()


if __name__ == "__main__":
    main()


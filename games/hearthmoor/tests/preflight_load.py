"""preflight page load: serve the game, open index.html once, wait for the title (assets + modules ready), fail on any JS error."""
import functools
import sys
import threading
import time
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from playwright.sync_api import sync_playwright

GAME = Path(__file__).resolve().parents[1]
ARGS = ["--use-angle=swiftshader", "--enable-unsafe-swiftshader", "--ignore-gpu-blocklist"]


class Quiet(SimpleHTTPRequestHandler):
    def log_message(self, *a):
        pass


def main():
    srv = ThreadingHTTPServer(("127.0.0.1", 0), functools.partial(Quiet, directory=str(GAME)))
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    url = f"http://127.0.0.1:{srv.server_address[1]}/index.html?nosw&peace"
    errors, t0, ok = [], time.time(), False
    with sync_playwright() as p:
        b = p.chromium.launch(args=ARGS)
        pg = b.new_page(viewport={"width": 960, "height": 540})
        pg.on("pageerror", lambda e: errors.append(f"PAGEERROR {e}"))
        pg.on("console", lambda m: errors.append(f"console.error {m.text}") if m.type == "error" else None)
        pg.on("requestfailed", lambda r: errors.append(f"REQUESTFAILED {r.url}"))
        try:
            pg.goto(url)
            ready = "(window.__hm && window.__hm.ready && window.__hd2d && window.__hd2d.ready && window.__hm.title && (window.__hd2d.frames || 0) >= 10) || false"
            while time.time() - t0 < 90 and not errors:   # stop at the first JS error instead of waiting out the timeout
                if pg.evaluate(ready):
                    ok = True; break
                pg.wait_for_timeout(250)   # poll pacing only
            if not ok and not errors:
                errors.append("title not ready in 90 s")
        except Exception as e:  # noqa: BLE001
            errors.append(f"load failed: {str(e).splitlines()[0][:200]}")
        b.close()
    srv.shutdown()
    for e in errors[:10]:
        print("preflight:", e[:300])
    print(f"preflight load: {'ok' if ok and not errors else 'FAIL'} ({time.time() - t0:.1f} s, {len(errors)} errors)", flush=True)
    sys.exit(0 if ok and not errors else 1)


if __name__ == "__main__":
    main()

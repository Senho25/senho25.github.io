import http.server, socketserver, os, json, time, threading
from urllib.parse import urlparse, parse_qs

class ThreadingHTTPServer(socketserver.ThreadingMixIn, http.server.HTTPServer):
    daemon_threads = True

os.chdir(os.path.dirname(os.path.abspath(__file__)))
PORT = 8080
DATA_FILE = os.path.join(os.getcwd(), "data.json")
VISITORS = {}
LOCK = threading.Lock()

# Default data structure
DEFAULT_DATA = {
    "users": [], "forums": [], "news": [], "clubs": [],
    "follows": {}, "user_follows": {}, "likes": {}, "news_likes": {},
    "news_saves": {}, "news_comment_likes": {}, "blocked": {},
    "reports": [], "session": None
}

def load_data():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                d = json.load(f)
                for k in DEFAULT_DATA:
                    if k not in d:
                        d[k] = DEFAULT_DATA[k]
                return d
        except:
            pass
    return dict(DEFAULT_DATA)

def save_data(d):
    with LOCK:
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(d, f, ensure_ascii=False, indent=2)

class Handler(http.server.SimpleHTTPRequestHandler):
    def _send_json(self, obj, code=200):
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(json.dumps(obj, ensure_ascii=False).encode())

    def do_GET(self):
        parsed = urlparse(self.path)
        ip = self.client_address[0]
        VISITORS[ip] = time.time()
        now = time.time()
        for k in list(VISITORS.keys()):
            if now - VISITORS[k] > 300:
                del VISITORS[k]

        # Stats
        if parsed.path == "/api/stats":
            online = sum(1 for t in VISITORS.values() if now - t < 120)
            d = load_data()
            self._send_json({
                "online": online, "total_ips": len(VISITORS),
                "uptime": int(now - START_TIME),
                "users": len(d["users"]), "clubs": len(d["clubs"]),
                "news": len(d["news"]), "forums": len(d["forums"])
            })
            return

        # Get all data
        if parsed.path == "/api/data":
            self._send_json(load_data())
            return

        # Admin: certify club
        if parsed.path.startswith("/api/admin/certify"):
            q = parse_qs(parsed.query)
            cid = q.get("id", [""])[0]
            cert = q.get("certified", ["1"])[0] == "1"
            d = load_data()
            c = next((x for x in d["clubs"] if x["id"] == cid), None)
            if c:
                c["certified"] = cert
                save_data(d)
                self._send_json({"ok": True})
            else:
                self._send_json({"ok": False, "error": "club not found"}, 404)
            return

        # Admin: pin news
        if parsed.path.startswith("/api/admin/pin-news"):
            q = parse_qs(parsed.query)
            nid = q.get("id", [""])[0]
            d = load_data()
            n = next((x for x in d["news"] if x["id"] == nid), None)
            if n:
                n["pinned"] = not n.get("pinned", False)
                save_data(d)
                self._send_json({"ok": True, "pinned": n["pinned"]})
            else:
                self._send_json({"ok": False}, 404)
            return

        # Admin: delete news
        if parsed.path.startswith("/api/admin/delete-news"):
            q = parse_qs(parsed.query)
            nid = q.get("id", [""])[0]
            d = load_data()
            d["news"] = [x for x in d["news"] if x["id"] != nid]
            save_data(d)
            self._send_json({"ok": True})
            return

        # Admin: delete forum
        if parsed.path.startswith("/api/admin/delete-forum"):
            q = parse_qs(parsed.query)
            fid = q.get("id", [""])[0]
            d = load_data()
            d["forums"] = [x for x in d["forums"] if x["id"] != fid]
            save_data(d)
            self._send_json({"ok": True})
            return

        # Admin: ban user
        if parsed.path.startswith("/api/admin/ban-user"):
            q = parse_qs(parsed.query)
            uid = q.get("id", [""])[0]
            banned = q.get("banned", ["1"])[0] == "1"
            d = load_data()
            u = next((x for x in d["users"] if x["id"] == uid), None)
            if u:
                u["banned"] = banned
                save_data(d)
                self._send_json({"ok": True})
            else:
                self._send_json({"ok": False}, 404)
            return

        return super().do_GET()

    def do_POST(self):
        parsed = urlparse(self.path)
        if parsed.path == "/api/data":
            length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(length)
            try:
                raw = json.loads(body)
                # Map localStorage keys -> canonical keys
                keymap = {
                    "aip_users": "users", "aip_forums": "forums", "aip_news": "news",
                    "aip_clubs": "clubs", "aip_session": "session"
                }
                new_data = load_data()
                for k, v in raw.items():
                    mapped = keymap.get(k, k)
                    if mapped in new_data:
                        new_data[mapped] = v
                save_data(new_data)
                self._send_json({"ok": True})
            except Exception as e:
                self._send_json({"ok": False, "error": str(e)}, 500)
            return
        self._send_json({"ok": False, "error": "not found"}, 404)

    def end_headers(self):
        self.send_header("Cache-Control", "no-cache")
        super().end_headers()

START_TIME = time.time()
print(f"AIP-Web serving on http://0.0.0.0:{PORT}")
with ThreadingHTTPServer(("0.0.0.0", PORT), Handler) as httpd:
    httpd.serve_forever()

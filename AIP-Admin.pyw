"""AIP-Web Admin Console v1.2.2 - Desktop Management"""
import tkinter as tk
from tkinter import ttk, messagebox
import subprocess, sys, os, threading, urllib.request, webbrowser, json

BASE = os.path.dirname(os.path.abspath(__file__))
PORT = 8080
URL = f"http://localhost:{PORT}"
PYTHONW = r"C:\Users\cmbc\AppData\Local\Doubao\User Data\sandbox_runtime\bases\c98c5042338ed152c6f10ecd8591889f\python\pythonw.exe"
FG = "#0f3d2e"; BG = "#1a5c42"; ACCENT = "#6bc49a"; BTN = "#2d7a58"; RED = "#c0392b"

def api(path):
    with urllib.request.urlopen(f"{URL}{path}", timeout=3) as r:
        return json.loads(r.read())

def api_get(path):
    try: return api(path)
    except: return None

class AdminApp:
    def __init__(self, root):
        self.root = root
        self.server_proc = None
        root.title("AIP-Web Admin Console")
        root.geometry("780x640")
        root.configure(bg=FG)

        # Top bar
        top = tk.Frame(root, bg=FG)
        top.pack(fill="x", padx=16, pady=(12, 6))
        tk.Label(top, text="AIP-WEB", font=("Georgia", 18, "bold italic"), fg="white", bg=FG).pack(side="left")
        self.status_dot = tk.Label(top, text="●", font=("Segoe UI", 12), fg="#e74c3c", bg=FG)
        self.status_dot.pack(side="right", padx=(8,0))
        self.status_lbl = tk.Label(top, text="OFFLINE", font=("Segoe UI", 9), fg="#aaa", bg=FG)
        self.status_lbl.pack(side="right")

        # Server controls
        sb = tk.Frame(root, bg=FG)
        sb.pack(fill="x", padx=16, pady=4)
        self.start_btn = tk.Button(sb, text="START", font=("Segoe UI", 9, "bold"), bg=BTN, fg="white",
                                   relief="flat", cursor="hand2", command=self.start_server, width=8)
        self.start_btn.pack(side="left", padx=2)
        self.stop_btn = tk.Button(sb, text="STOP", font=("Segoe UI", 9, "bold"), bg=RED, fg="white",
                                  relief="flat", cursor="hand2", command=self.stop_server, width=8, state="disabled")
        self.stop_btn.pack(side="left", padx=2)
        self.open_btn = tk.Button(sb, text="Open Site", font=("Segoe UI", 9), bg=BG, fg="white",
                                  relief="flat", cursor="hand2", command=lambda: webbrowser.open(f"{URL}/"))
        self.open_btn.pack(side="left", padx=2)
        self.refresh_btn = tk.Button(sb, text="Refresh", font=("Segoe UI", 9), bg=BG, fg="white",
                                     relief="flat", cursor="hand2", command=self.load_all)
        self.refresh_btn.pack(side="left", padx=2)
        self.online_lbl = tk.Label(sb, text="", font=("Segoe UI", 9), fg=ACCENT, bg=FG)
        self.online_lbl.pack(side="right")

        # Notebook tabs
        nb = ttk.Notebook(root)
        nb.pack(fill="both", expand=True, padx=16, pady=8)

        # Clubs tab
        self.clubs_frame = tk.Frame(nb, bg="white")
        nb.add(self.clubs_frame, text="  Clubs  ")
        self.clubs_canvas = tk.Canvas(self.clubs_frame, bg="white", highlightthickness=0)
        self.clubs_canvas.pack(side="left", fill="both", expand=True)
        self.clubs_inner = tk.Frame(self.clubs_canvas, bg="white")
        self.clubs_canvas.create_window((0,0), window=self.clubs_inner, anchor="nw")
        self.clubs_canvas.bind("<Configure>", lambda e: self.clubs_canvas.itemconfig("all", width=e.width))

        # News tab
        self.news_frame = tk.Frame(nb, bg="white")
        nb.add(self.news_frame, text="  News  ")
        self.news_canvas = tk.Canvas(self.news_frame, bg="white", highlightthickness=0)
        self.news_canvas.pack(side="left", fill="both", expand=True)
        self.news_inner = tk.Frame(self.news_canvas, bg="white")
        self.news_canvas.create_window((0,0), window=self.news_inner, anchor="nw")

        # Forums tab
        self.forums_frame = tk.Frame(nb, bg="white")
        nb.add(self.forums_frame, text="  Forums  ")
        self.forums_canvas = tk.Canvas(self.forums_frame, bg="white", highlightthickness=0)
        self.forums_canvas.pack(side="left", fill="both", expand=True)
        self.forums_inner = tk.Frame(self.forums_canvas, bg="white")
        self.forums_canvas.create_window((0,0), window=self.forums_inner, anchor="nw")

        # Users tab
        self.users_frame = tk.Frame(nb, bg="white")
        nb.add(self.users_frame, text="  Users  ")
        self.users_canvas = tk.Canvas(self.users_frame, bg="white", highlightthickness=0)
        self.users_canvas.pack(side="left", fill="both", expand=True)
        self.users_inner = tk.Frame(self.users_canvas, bg="white")
        self.users_canvas.create_window((0,0), window=self.users_inner, anchor="nw")

        self.root.after(800, self.poll)

    def start_server(self):
        self.start_btn.config(state="disabled", text="...")
        self.status_lbl.config(text="STARTING...")
        threading.Thread(target=self._start_thr, daemon=True).start()

    def _start_thr(self):
        try:
            exe = PYTHONW if os.path.exists(PYTHONW) else sys.executable
            self.server_proc = subprocess.Popen([exe, os.path.join(BASE, "serve.py")], cwd=BASE,
                creationflags=subprocess.CREATE_NO_WINDOW, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("Error", str(e)))

    def stop_server(self):
        if self.server_proc:
            try: self.server_proc.terminate()
            except: pass
            self.server_proc = None
        self.status_lbl.config(text="OFFLINE")
        self.status_dot.config(fg="#e74c3c")
        self.start_btn.config(state="normal", text="START")
        self.stop_btn.config(state="disabled")
        self.online_lbl.config(text="")

    def poll(self):
        threading.Thread(target=self._poll_thr, daemon=True).start()
        self.root.after(3000, self.poll)

    def _poll_thr(self):
        s = api_get("/api/stats")
        if s:
            self.root.after(0, lambda: self._online(s))
        else:
            self.root.after(0, self._offline)

    def _online(self, s):
        self.status_lbl.config(text="ONLINE")
        self.status_dot.config(fg="#2ecc71")
        self.start_btn.config(state="disabled", text="START")
        self.stop_btn.config(state="normal")
        self.online_lbl.config(text=f"Online: {s['online']}  ·  Users: {s['users']}  ·  Clubs: {s['clubs']}  ·  News: {s['news']}")
        self.load_all()

    def _offline(self):
        if not self.server_proc:
            self.status_lbl.config(text="OFFLINE")
            self.status_dot.config(fg="#e74c3c")
            self.start_btn.config(state="normal", text="START")
            self.stop_btn.config(state="disabled")

    def load_all(self):
        threading.Thread(target=self._load_thr, daemon=True).start()

    def _load_thr(self):
        d = api_get("/api/data")
        if d:
            self.root.after(0, lambda: self._render(d))

    def _render(self, d):
        self._render_clubs(d.get("clubs", []))
        self._render_news(d.get("news", []))
        self._render_forums(d.get("forums", []))
        self._render_users(d.get("users", []))

    def _clear(self, frame):
            for w in frame.winfo_children(): w.destroy()

    def _render_clubs(self, clubs):
        self._clear(self.clubs_inner)
        for c in clubs:
            row = tk.Frame(self.clubs_inner, bg="white", pady=4)
            row.pack(fill="x", padx=8)
            name = c.get("name","?")
            cert = c.get("certified", False)
            tag = " [CERTIFIED]" if cert else ""
            tk.Label(row, text=name + tag, font=("Segoe UI", 10, "bold" if cert else "normal"),
                     fg="#d4a017" if cert else "#222", bg="white").pack(side="left")
            tk.Label(row, text=f"  ({len(c.get('members',[]))} members)", font=("Segoe UI", 8),
                     fg="#888", bg="white").pack(side="left")
            btn_txt = "Revoke" if cert else "Grant AIP"
            btn_clr = "#888" if cert else BTN
            tk.Button(row, text=btn_txt, font=("Segoe UI", 8), bg=btn_clr, fg="white", relief="flat",
                      cursor="hand2", padx=8, command=lambda cid=c["id"], cert=cert: self.do_certify(cid, not cert)).pack(side="right")
        tk.Frame(self.clubs_inner, bg="white", height=8).pack()

    def _render_news(self, news):
        self._clear(self.news_inner)
        for n in sorted(news, key=lambda x: -x.get("createdAt",0)):
            row = tk.Frame(self.news_inner, bg="white", pady=3)
            row.pack(fill="x", padx=8)
            pinned = n.get("pinned", False)
            tag = " [PINNED]" if pinned else ""
            tk.Label(row, text=(n.get("title","?") or "?")[:60] + tag,
                     font=("Segoe UI", 9, "bold" if pinned else "normal"),
                     fg=FG if pinned else "#222", bg="white", wraplength=400, justify="left").pack(side="left")
            tk.Button(row, text="Pin" if not pinned else "Unpin", font=("Segoe UI", 8),
                      bg=BTN if not pinned else "#888", fg="white", relief="flat", cursor="hand2",
                      padx=6, command=lambda nid=n["id"]: self.do_pin_news(nid)).pack(side="right", padx=2)
            tk.Button(row, text="Delete", font=("Segoe UI", 8), bg=RED, fg="white", relief="flat",
                      cursor="hand2", padx=6, command=lambda nid=n["id"], t=n.get("title",""): self.do_delete_news(nid, t)).pack(side="right", padx=2)
        tk.Frame(self.news_inner, bg="white", height=8).pack()

    def _render_forums(self, forums):
        self._clear(self.forums_inner)
        for f in forums:
            row = tk.Frame(self.forums_inner, bg="white", pady=3)
            row.pack(fill="x", padx=8)
            posts = len(f.get("posts", []))
            tk.Label(row, text=f.get("name","?")[:50], font=("Segoe UI", 9), fg="#222", bg="white").pack(side="left")
            tk.Label(row, text=f" ({posts} posts)", font=("Segoe UI", 8), fg="#888", bg="white").pack(side="left")
            tk.Button(row, text="Delete", font=("Segoe UI", 8), bg=RED, fg="white", relief="flat",
                      cursor="hand2", padx=6, command=lambda fid=f["id"], n=f.get("name",""): self.do_delete_forum(fid, n)).pack(side="right")
        tk.Frame(self.forums_inner, bg="white", height=8).pack()

    def _render_users(self, users):
        self._clear(self.users_inner)
        for u in users:
            row = tk.Frame(self.users_inner, bg="white", pady=3)
            row.pack(fill="x", padx=8)
            banned = u.get("banned", False)
            role = u.get("role", "member")
            tag = " [BANNED]" if banned else f" [{role}]"
            tk.Label(row, text=u.get("username","?") + tag,
                     font=("Segoe UI", 9, "bold" if banned else "normal"),
                     fg=RED if banned else "#222", bg="white").pack(side="left")
            if role != "admin":
                tk.Button(row, text="Unban" if banned else "Ban", font=("Segoe UI", 8),
                          bg=BTN if banned else RED, fg="white", relief="flat", cursor="hand2",
                          padx=6, command=lambda uid=u["id"], b=banned: self.do_ban(uid, not b)).pack(side="right")
        tk.Frame(self.users_inner, bg="white", height=8).pack()

    def do_certify(self, cid, cert):
        api_get(f"/api/admin/certify?id={cid}&certified={1 if cert else 0}")
        self.load_all()

    def do_pin_news(self, nid):
        api_get(f"/api/admin/pin-news?id={nid}")
        self.load_all()

    def do_delete_news(self, nid, title):
        if messagebox.askyesno("Delete", f"Delete news: {title[:50]}?"):
            api_get(f"/api/admin/delete-news?id={nid}")
            self.load_all()

    def do_delete_forum(self, fid, name):
        if messagebox.askyesno("Delete", f"Delete forum: {name[:50]}?"):
            api_get(f"/api/admin/delete-forum?id={fid}")
            self.load_all()

    def do_ban(self, uid, ban):
        if ban and not messagebox.askyesno("Ban", "Ban this user?"):
            return
        api_get(f"/api/admin/ban-user?id={uid}&banned={1 if ban else 0}")
        self.load_all()

if __name__ == "__main__":
    root = tk.Tk()
    app = AdminApp(root)
    root.mainloop()

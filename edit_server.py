#!/usr/bin/env python3
"""Local editing server for the Alcuin site (alcuinproject.com).

Serves the built site at http://localhost:8788 with an "Edit text" mode
layered on top, the same way the devotional editor does. Clicking a
heading, paragraph, list item, button label, or nav link makes it
editable in place; Save writes the change back to the matching line in
copy/*.md (the source of truth), rebuilds the site with
build_redesign.py, and reloads the page.

Publish runs the Cloudflare Pages deploy that launched the site
(`npx wrangler pages deploy redesign --project-name=alcuinproject`).
A dry run first lists the files that differ from the last deploy, which
is kept as a snapshot in .published/.

The copy folder and the story file are backed up to
.backups/copy-<timestamp>/ once per server start, before any write.

    python3 edit_server.py             # start, open the browser
    python3 edit_server.py --no-open   # start without opening a browser
    python3 edit_server.py --snapshot  # re-seed .published/ from redesign/
                                       # (only after confirming redesign/
                                       # matches what is live)
"""

import functools
import html
import http.server
import importlib
import json
import os
import re
import shutil
import subprocess
import sys
import threading
import time
import urllib.parse
import webbrowser

import build_redesign

HERE = os.path.dirname(os.path.abspath(__file__))
COPY = os.path.join(HERE, "copy")
EDITOR = os.path.join(HERE, "editor")
OUT = str(build_redesign.OUT)
PUBLISHED = os.path.join(HERE, ".published")
PORT = int(os.environ.get("ALCUIN_PORT", "8788"))
LOCK = threading.Lock()
# Folder holding node/npx for the wrangler deploy; override with ALCUIN_NODE_BIN.
NODE_BIN = os.environ.get("ALCUIN_NODE_BIN", os.path.expanduser("~/.local/node/bin"))
PROJECT_NAME = "alcuinproject"
SITE_URL = "https://alcuinproject.com"

MIME = {
    ".html": "text/html; charset=utf-8",
    ".css": "text/css; charset=utf-8",
    ".js": "application/javascript; charset=utf-8",
    ".png": "image/png",
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".svg": "image/svg+xml",
    ".pdf": "application/pdf",
    ".txt": "text/plain; charset=utf-8",
    ".xml": "application/xml; charset=utf-8",
    ".webp": "image/webp",
    ".ico": "image/x-icon",
}

INJECT = ('<link rel="stylesheet" href="/__edit/edit.css">'
          '<script src="/__edit/edit.js"></script></body>')


# ------------------------------------------------------------ content model
#
# Every copy file is read with line numbers kept, mirroring what
# build_redesign.load_slots() and md() do to it, so that each rendered
# fragment can be traced back to the source lines that produced it.

def source_files():
    """(label, absolute path, kind) for every file the builder reads."""
    out = []
    src = open(build_redesign.__file__, encoding="utf-8").read()
    used = set(re.findall(r'load_slots\("([^"]+)"\)', src)) | {"alerts.md"}
    for fn in sorted(os.listdir(COPY)):
        p = os.path.join(COPY, fn)
        if fn in used and os.path.isfile(p):
            out.append((fn, p, "alerts" if fn == "alerts.md" else "slots"))
    for sub in ("guides", "posts"):
        d = os.path.join(COPY, sub)
        if os.path.isdir(d):
            for fn in sorted(os.listdir(d)):
                if fn.endswith(".md") and fn != "README.md":
                    out.append((sub + "/" + fn, os.path.join(d, fn), "slots"))
    story = str(build_redesign.STORY_FILE)
    out.append((os.path.basename(story), story, "story"))
    return out


def strip_comments_keep_lines(raw):
    """Remove <!-- --> blocks without shifting line numbers.

    Returns (lines, dirty) where dirty is the set of line indexes a
    comment touched. Those lines are matched but never rewritten in
    place, so a comment can't be clobbered by a save.
    """
    dirty = set()

    def repl(m):
        start = raw.count("\n", 0, m.start())
        n = m.group(0).count("\n")
        dirty.update(range(start, start + n + 1))
        return "\n" * n
    text = re.sub(r"<!--.*?-->", repl, raw, flags=re.S)
    return text.split("\n"), dirty


def slot_bodies(lines, kind):
    """Yield (slot_name, [(lineno, text), ...]) as the builder sees them."""
    if kind == "story":
        body, seen_title = [], False
        for i, l in enumerate(lines):
            if not seen_title and re.match(r"^# ", l):
                seen_title = True
                continue
            body.append((i, l))
        yield "body", body
        return
    current, buf = None, []
    for i, l in enumerate(lines):
        if re.match(r"^#(?!#)", l):
            continue
        m = re.match(r"^## (.+)$", l)
        if m:
            if current:
                yield current, buf
            current, buf = m.group(1).strip(), []
        elif current is not None:
            buf.append((i, l))
    if current:
        yield current, buf


def blocks(body):
    """Group a slot body into paragraphs the way md() does."""
    cur = []
    for ln, text in body:
        if text.strip():
            cur.append((ln, text.rstrip()))
        elif cur:
            yield cur
            cur = []
    if cur:
        yield cur


ROW_RE = re.compile(r"^(- \*\*)(.+?)(\*\*\s*[—-]?\s*)(.*)$")
NUM_RE = re.compile(r"^(\d+\. )(.*)$")

inline = build_redesign.inline
esc = build_redesign.esc


def candidates():
    """Every editable fragment: dicts with file, first, last, kind, html."""
    out = []

    def add_base(label, path, dirty, first, last, kind, rendered, **extra):
        c = {"label": label, "path": path, "first": first, "last": last,
             "kind": kind, "html": norm(rendered), "slot": extra.pop("slot", ""),
             "id": "%s:%d:%s" % (label, first, kind),
             "dirty": any(i in dirty for i in range(first, last + 1))}
        c.update(extra)
        out.append(c)

    add = add_base
    for label, path, kind in source_files():
        with open(path, encoding="utf-8") as fh:
            raw = fh.read()
        lines, dirty = strip_comments_keep_lines(raw)
        if kind == "alerts":
            for i, l in enumerate(lines):
                if l.startswith("#"):
                    continue
                m = re.match(r"^([a-z-]+):\s*(.*)$", l)
                if m and m.group(2).strip():
                    add(label, path, dirty, i, i, "kv", esc(m.group(2)),
                        key=m.group(1), slot=m.group(1))
            continue
        for slot, body in slot_bodies(lines, kind):
            if slot.startswith("config-"):
                continue
            add = functools.partial(add_base, slot=slot)
            for blk in blocks(body):
                texts = [t for _, t in blk]
                first, last = blk[0][0], blk[-1][0]
                if len(blk) == 1 and texts[0].startswith("### "):
                    add(label, path, dirty, first, last, "h3",
                        inline(texts[0][4:]))
                elif len(blk) == 1 and texts[0].startswith("## "):
                    add(label, path, dirty, first, last, "h2",
                        inline(texts[0][3:]))
                elif all(t.startswith("> ") for t in texts):
                    add(label, path, dirty, first, last, "quote",
                        inline(" ".join(t[2:] for t in texts)))
                elif all(t.startswith("- ") or t.startswith("* ")
                         for t in texts):
                    for ln, t in blk:
                        add(label, path, dirty, ln, ln, "li", inline(t[2:]),
                            bullet=t[:2])
                        m = ROW_RE.match(t)
                        if m:
                            name, rest = m.group(2), m.group(4)
                            add(label, path, dirty, ln, ln, "rowh",
                                inline(name.rstrip(".")),
                                parts=list(m.groups()))
                            add(label, path, dirty, ln, ln, "rowp",
                                inline(rest), parts=list(m.groups()))
                elif all(NUM_RE.match(t) for t in texts):
                    for ln, t in blk:
                        m = NUM_RE.match(t)
                        add(label, path, dirty, ln, ln, "ol",
                            inline(m.group(2)), prefix=m.group(1))
                else:
                    add(label, path, dirty, first, last, "p",
                        inline(" ".join(texts)))
    return out


# ------------------------------------------------------- matching machinery

def norm(h):
    """Canonical form for comparing server-rendered vs browser innerHTML."""
    h = re.sub(r"<br\s*/?>", " ", h, flags=re.I)
    h = re.sub(r"</?(div|p|span)(\s[^>]*)?>", " ", h, flags=re.I)
    h = re.sub(r'<a\s[^>]*?href="([^"]*)"[^>]*>', r'<a href="\1">', h,
               flags=re.I)
    h = re.sub(r"<(/?)b(\s[^>]*)?>", r"<\1strong>", h, flags=re.I)
    h = re.sub(r"<(/?)i(\s[^>]*)?>", r"<\1em>", h, flags=re.I)
    h = re.sub(r"<(strong|em)\s[^>]*>", r"<\1>", h, flags=re.I)
    h = html.unescape(h).replace("\xa0", " ")
    h = re.sub(r"\s+", " ", h)
    h = re.sub(r"\s*<\s*", "<", h)
    h = re.sub(r"\s*>\s*", ">", h)
    return h.strip()


def own_labels(slug):
    """Copy files a page most plausibly draws from, used to break ties."""
    own = {"global.md"}
    if slug == "index":
        own.add("home.md")
    elif slug == "our-story":
        own.add(os.path.basename(str(build_redesign.STORY_FILE)))
    elif slug.startswith("blog-"):
        own.add("posts/" + slug[5:] + ".md")
        own.add("blog.md")
    elif slug == "guides":
        own.update({"guides_index.md", "alerts.md"})
    else:
        own.add(slug + ".md")
        own.add("guides/" + slug + ".md")
    return own


# --------------------------------------------------------- writing changes

def to_markup(h, allow_markup=True):
    """Browser innerHTML back to copy-file markup (** and *, [..](..))."""
    h = re.sub(r"<br\s*/?>", " ", h, flags=re.I)
    h = re.sub(r'<a\s[^>]*?href="([^"]*)"[^>]*>(.*?)</a>', r"[\2](\1)",
               h, flags=re.I | re.S)
    if allow_markup:
        h = re.sub(r"<\s*(strong|b)(\s[^>]*)?>(.*?)</\s*\1\s*>", r"**\3**",
                   h, flags=re.I | re.S)
        h = re.sub(r"<\s*(em|i)(\s[^>]*)?>(.*?)</\s*\1\s*>", r"*\3*",
                   h, flags=re.I | re.S)
    h = re.sub(r"<[^>]+>", " ", h)
    h = html.unescape(h).replace("\xa0", " ")
    return re.sub(r"\s+", " ", h).strip()


def build_new_line(c, new_html):
    kind = c["kind"]
    if kind == "kv":
        return "%s: %s" % (c["key"], to_markup(new_html, False))
    text = to_markup(new_html)
    if not text:
        return ""
    if kind == "h3":
        return "### " + text
    if kind == "h2":
        return "## " + text
    if kind == "quote":
        return "> " + text
    if kind == "li":
        return c["bullet"] + text
    if kind == "ol":
        return c["prefix"] + text
    if kind == "rowh":
        lead, name, sep, rest = c["parts"]
        dot = "." if name.endswith(".") else ""
        return "%s%s%s%s%s" % (lead, text.rstrip("."), dot, sep, rest)
    if kind == "rowp":
        lead, name, sep, _rest = c["parts"]
        return "%s%s%s%s" % (lead, name, sep, text)
    return text                                   # plain paragraph


def write_block(path, first, last, new_line):
    with open(path, encoding="utf-8") as fh:
        lines = fh.read().split("\n")
    lines[first:last + 1] = [new_line]
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines))
    os.replace(tmp, path)


def rebuild():
    # pick up edits to build_redesign.py without a server restart
    importlib.reload(build_redesign)
    global inline, esc
    inline, esc = build_redesign.inline, build_redesign.esc
    cwd = os.getcwd()
    os.chdir(HERE)
    try:
        build_redesign.main()
    finally:
        os.chdir(cwd)


def handle_save(data):
    slug = data.get("page", "")
    old = norm(data.get("old_html", ""))
    new_html = data.get("new_html", "")
    if not old:
        return {"ok": False, "error": "Nothing to match against."}

    matches = [c for c in candidates() if c["html"] == old]
    if not matches:
        return {"ok": False, "error":
                "Couldn't map this text back to a line in copy/*.md. "
                "It may be assembled from more than one place, or written "
                "into the build script itself. Make this edit in the "
                "copy file."}
    choice = data.get("choice")
    if choice:
        matches = [c for c in matches if c["id"] == choice]
        if not matches:
            return {"ok": False, "error": "That choice no longer exists. "
                    "Reload the page and try again."}
    distinct = {(c["path"], c["first"]) for c in matches}
    if len(distinct) > 1:
        own = own_labels(slug)
        narrowed = [c for c in matches if c["label"] in own]
        if len({(c["path"], c["first"]) for c in narrowed}) == 1:
            matches = narrowed
        else:
            pool = narrowed or matches
            seen, options = set(), []
            for c in pool:
                if (c["path"], c["first"]) in seen:
                    continue
                seen.add((c["path"], c["first"]))
                options.append({"id": c["id"], "label": c["label"],
                                "slot": c["slot"], "line": c["first"] + 1})
            return {"ok": False, "choose": options}

    c = matches[0]
    if c["dirty"]:
        return {"ok": False, "error":
                "This line shares its source line with an editorial "
                "comment (<!-- -->), so the editor won't rewrite it. Make "
                "this edit in %s, line %d." % (c["label"], c["first"] + 1)}
    new_line = build_new_line(c, new_html)
    if not new_line.strip() or (c["kind"] == "kv" and
                                not new_line.split(":", 1)[1].strip()):
        return {"ok": False, "error":
                "That would empty the line out. To delete a line, do it "
                "in the copy file."}

    write_block(c["path"], c["first"], c["last"], new_line)
    rebuild()
    return {"ok": True,
            "saved": new_line,
            "file": c["label"],
            "line": c["first"] + 1}


# --------------------------------------------------------------- publish

def _run(cmd, cwd, env=None, timeout=300):
    try:
        p = subprocess.run(cmd, cwd=cwd, env=env, capture_output=True,
                           text=True, timeout=timeout)
    except subprocess.TimeoutExpired:
        return 1, "timed out after %ds" % timeout
    return p.returncode, (p.stdout + p.stderr).strip()


def unpublished_files():
    """Files that differ between a fresh build and the last deploy."""
    rebuild()
    if not os.path.isdir(PUBLISHED):
        return None
    # -c compares content: the rebuild rewrites every file, so mtimes
    # alone would list the whole site as changed
    code, out = _run(["rsync", "-rc", "--delete", "--dry-run", "-i",
                      OUT + "/", PUBLISHED + "/"], HERE)
    changed = []
    for line in out.splitlines():
        parts = line.split(None, 1)
        if (len(parts) == 2 and parts[0][0] in "<>*c"
                and not parts[1].endswith("/")):
            changed.append(parts[1])
    return changed


def snapshot():
    """Record redesign/ as what is live, for the next dry run."""
    os.makedirs(PUBLISHED, exist_ok=True)
    _run(["rsync", "-a", "--delete", OUT + "/", PUBLISHED + "/"], HERE)


def handle_publish(data):
    dry = bool(data.get("dry"))
    changed = unpublished_files()
    if changed is None:
        return {"ok": False, "error":
                "No record of the last deploy (.published/ is missing). "
                "Run  python3 edit_server.py --snapshot  once, after "
                "confirming redesign/ matches the live site."}
    if dry:
        return {"ok": True, "dry": True, "changed": changed}
    if not changed:
        return {"ok": True, "changed": [],
                "message": "The published site already matches. Nothing to push."}
    env = dict(os.environ)
    env["PATH"] = NODE_BIN + ":" + env.get("PATH", "") + ":/usr/bin:/usr/local/bin"
    env.pop("npm_config_prefix", None)
    code, out = _run(["npx", "--yes", "wrangler", "pages", "deploy", OUT,
                      "--project-name=" + PROJECT_NAME, "--commit-dirty=true"],
                     HERE, env)
    if code != 0:
        return {"ok": False, "error": "wrangler deploy failed:\n" + out[-1500:]}
    snapshot()
    m = re.search(r"https://\S+\.pages\.dev", out)
    return {"ok": True, "changed": changed, "log": out[-1500:],
            "deployment": m.group(0) if m else "", "url": SITE_URL}


# ------------------------------------------------------------------ server

class Handler(http.server.BaseHTTPRequestHandler):

    def log_message(self, fmt, *args):        # quiet the request log
        pass

    def _send(self, code, ctype, body):
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        path = urllib.parse.urlparse(self.path).path
        if path in ("", "/"):
            path = "/index.html"
        if path.startswith("/__edit/"):
            base, rel = EDITOR, path[len("/__edit/"):]
        else:
            base, rel = OUT, path.lstrip("/")
            # the live site serves /about for about.html; do the same
            if not os.path.splitext(rel)[1] and \
                    os.path.isfile(os.path.join(base, rel + ".html")):
                rel += ".html"
        base = os.path.realpath(base)
        fp = os.path.realpath(os.path.join(base, rel))
        if not fp.startswith(base + os.sep) or not os.path.isfile(fp):
            fp404 = os.path.join(OUT, "404.html")
            if os.path.isfile(fp404):
                with open(fp404, "rb") as fh:
                    body = fh.read().replace(b"</body>", INJECT.encode(), 1)
                self._send(404, MIME[".html"], body)
            else:
                self._send(404, "text/plain; charset=utf-8", b"not found")
            return
        ext = os.path.splitext(fp)[1].lower()
        ctype = MIME.get(ext, "application/octet-stream")
        with open(fp, "rb") as fh:
            body = fh.read()
        if ext == ".html":
            body = body.replace(b"</body>", INJECT.encode("utf-8"), 1)
        self._send(200, ctype, body)

    def do_POST(self):
        path = urllib.parse.urlparse(self.path).path
        if path not in ("/api/save", "/api/publish"):
            self._send(404, "text/plain; charset=utf-8", b"not found")
            return
        try:
            n = int(self.headers.get("Content-Length", 0))
            data = json.loads(self.rfile.read(n).decode("utf-8"))
            with LOCK:
                if path == "/api/publish":
                    result = handle_publish(data)
                else:
                    result = handle_save(data)
        except Exception as e:                              # noqa: BLE001
            result = {"ok": False, "error": "Server error: %s" % e}
        self._send(200, "application/json; charset=utf-8",
                   json.dumps(result).encode("utf-8"))


def backup_content():
    ts = time.strftime("%Y%m%d-%H%M%S")
    dst = os.path.join(HERE, ".backups", "copy-" + ts)
    shutil.copytree(COPY, dst)
    shutil.copy(str(build_redesign.STORY_FILE), dst)
    return dst


def main():
    if "--snapshot" in sys.argv:
        rebuild()
        snapshot()
        print("recorded redesign/ as the published state in .published/")
        return
    dst = backup_content()
    print("copy backed up to", os.path.relpath(dst, HERE))
    rebuild()
    if not os.path.isdir(PUBLISHED):
        print("NOTE: no .published/ snapshot yet; Publish will ask for one")
    try:
        server = http.server.ThreadingHTTPServer(("127.0.0.1", PORT), Handler)
    except OSError:
        sys.exit("Port %d is already in use. Is the editor already running? "
                 "Close it, or set ALCUIN_PORT to another port." % PORT)
    url = "http://localhost:%d" % PORT
    print("Alcuin editing server ready:", url)
    if "--no-open" not in sys.argv:
        threading.Timer(0.6, lambda: webbrowser.open(url)).start()
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nstopped; every saved edit is in copy/*.md")


if __name__ == "__main__":
    main()

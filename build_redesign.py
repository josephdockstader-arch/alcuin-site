#!/usr/bin/env python3
"""Build the Alcuin site from plain copy files.

Version 3 (2026-09-08): implements Joseph's adversarial-review package
(alcuin-website-copy.md + alcuin-review-and-claude-code-brief.md,
supplied in-session) plus his technology-solutions amendment.
Copy: site/copy/*.md (## slot headers). Story: newest our_story_draft_v*.md.
Output: site/redesign/*.html. Edit copy, rerun, reload.

    python3 build_redesign.py

Prior builder preserved at
../superseded-2026-09-08/build_redesign_pre-adversarial.py
(its splash section restores the retired entry-curtain if Joseph ever
wants it back).
"""

import datetime
import datetime as dt
import re
import shutil
import subprocess

from PIL import Image
from pathlib import Path
from urllib.parse import quote

HERE = Path(__file__).resolve().parent
COPY = HERE / "copy"
OUT = HERE / "redesign"
STORY_CANDIDATES = sorted(HERE.glob("our_story_draft_v*.md"),
                          key=lambda p: int(re.search(r"v(\d+)", p.name).group(1)))
STORY_FILE = STORY_CANDIDATES[-1]
# Image sources live in ../content-drop in the working project. The public
# repo carries the same files in images/, so either location works.
def _first_existing(*paths):
    return next((p for p in paths if p.exists()), paths[0])

HEADSHOT = _first_existing(
    HERE.parent / "content-drop" / "headshot_ai_render_2026-08-25.png",
    HERE / "images" / "headshot_ai_render_2026-08-25.png")

# Room photograph for the homepage band. Joseph is still iterating on the
# source image (2026-09-18) -- drop a replacement at this path and
# rebuild. Widths are generated from it; nothing is upscaled, so a source
# narrower than a listed width is simply skipped.
CLASSROOM = _first_existing(
    HERE.parent / "content-drop" / "classroom_2026-09-18.jpg",
    HERE / "images" / "classroom_2026-09-18.jpg")
CLASSROOM_WIDTHS = (900, 1400, 2000, 2800)

# The three adopted AI Norms designs (../norms-poster/README.md, ruling
# 2026-09-09). The site publishes DERIVED previews only: downscaled and
# watermarked. The print replicas stay in ~/Downloads and are supplied
# on purchase -- never copied into redesign/assets/.
POSTER_SRC = HERE.parent / "norms-poster" / "source-images"
POSTERS = [
    ("ledger", "Alcuin_AI_Norms_C_MasterLogo.png"),
    ("gallery", "Alcuin_AI_Norms_B_Cream_MasterLogo.png"),
    ("chalk", "Alcuin_AI_Norms_B_Dark_MasterLogo.png"),
]
# Thumbnails render at ~330px wide in the grid, so they ship at 2x
# (1000px tall / ~667 wide) -- at 440 they were upscaled by every retina
# screen and looked dingy (Joseph, 2026-09-18).
POSTER_THUMB_H = 1000
POSTER_PREVIEW_H = 1240
WATERMARK_FONT = "/System/Library/Fonts/Supplemental/Georgia.ttf"

# Blog lead cards. Drawn at build time from each post's own title -- no
# photography and no stock, so a link post never borrows the publisher's
# image, and the card is what a share preview shows. 1200x630 is the
# open-graph standard; the index renders it at ~240px.
CARD_W, CARD_H = 1200, 630
CARD_SERIF = "/System/Library/Fonts/Supplemental/Georgia Bold.ttf"
CARD_SANS = "/System/Library/Fonts/Supplemental/Arial Bold.ttf"
TEAL_RGB = (23, 49, 59)
CREAM_RGB = (246, 241, 229)
EMBER_RGB = (232, 80, 30)
SEAFOAM_RGB = (169, 195, 192)
# The favicon geometry in cream, rendered once per build by headless
# Chrome (no SVG library in this environment) and cached in .build/.
MARK_SVG = ("<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 200 200'"
            " width='400' height='400'>"
            "<g fill='none' stroke='#f6f1e5' stroke-width='12'"
            " stroke-linecap='round'>"
            "<path d='M40 140 C70 110 90 130 110 105 C130 80 150 95 164 78'/>"
            "<path d='M40 118 C68 92 88 110 108 86 C126 65 144 78 160 62'/>"
            "<path d='M40 160 C74 132 96 150 118 126 C136 107 152 116 164 102'/>"
            "</g><line x1='118' y1='158' x2='160' y2='158' stroke='#e8501e'"
            " stroke-width='16' stroke-linecap='round'/></svg>")
CHROME = ("/Applications/Google Chrome.app/Contents/MacOS/Google Chrome")

# Pre-launch: every page carries a noindex meta so a staging deploy never
# gets indexed. Flip to False at launch (one line; decision 2026-09-10 —
# nothing ships muted, so the whole site goes indexable together).
# 2026-09-18: noindex lifted for launch. Setting this back to True
# re-stamps <meta name="robots" content="noindex"> on every page and
# makes robots.txt disallow everything -- use it for a staging copy.
PRELAUNCH = False
SHOW_SPLASH = False  # home entry curtain; off since 2026-09-24

# Absolute origin, needed for canonical URLs, sitemap entries and the
# og:image (social crawlers will not resolve a relative image path).
SITE_URL = "https://alcuinproject.com"

# ---------------------------------------------------------------- parsing

def load_slots(name):
    """Parse a copy file into ## slot -> text.

    Editorial notes are stripped, not rendered: `#` lines and <!-- -->
    blocks are comments anywhere in the file. Before 2026-09-18 only the
    lines above the first slot were dropped, so a note written between
    two slots leaked into the page above it -- which silently corrupted
    contact.md's config-schedule-url (the booking link) when the
    advisory copy landed there.
    """
    slots, current, buf = {}, None, []
    raw = re.sub(r"<!--.*?-->", "", (COPY / name).read_text(), flags=re.S)
    for line in raw.splitlines():
        if re.match(r"^#(?!#)", line):
            continue
        m = re.match(r"^## (.+)$", line)
        if m:
            if current:
                slots[current] = "\n".join(buf).strip()
            current, buf = m.group(1).strip(), []
        elif current is not None:
            buf.append(line)
    if current:
        slots[current] = "\n".join(buf).strip()
    return slots


def esc(text):
    """Escape for both text and attribute contexts.

    Quotes were not escaped before 2026-09-18, so a copy line containing
    a double quote silently truncated whatever attribute it was written
    into. The MIT post's summary quotes "cognitive surrender", and its
    meta description was cut to 50 characters at that quote -- with the
    rest of the sentence leaking into the tag as stray markup. Same
    exposure applied to alt text, aria-label and every og: tag.
    """
    return (text.replace("&", "&amp;").replace("<", "&lt;")
                .replace(">", "&gt;").replace('"', "&quot;")
                .replace("'", "&#39;"))


def inline(text):
    text = re.sub(r"<!--.*?-->", "", text, flags=re.S).strip()
    text = esc(text)
    text = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", text)
    text = re.sub(r"\*(.+?)\*", r"<em>\1</em>", text)
    # [label](href) -- added 2026-09-18 so copy can cross-link pages.
    # Only relative .html targets and https URLs; anything else is left
    # as literal text rather than becoming a link of unknown shape.
    def link(m):
        label, href = m.group(1), m.group(2)
        if re.fullmatch(r"[a-z0-9-]+\.html(?:#[a-z0-9-]+)?", href):
            return f'<a href="{href}">{label}</a>'
        if href.startswith("https://"):
            return (f'<a href="{href}" target="_blank" '
                    f'rel="noopener noreferrer">{label}</a>')
        return m.group(0)
    return re.sub(r"\[([^\]]+)\]\(([^)]+)\)", link, text)


NUM_RE = re.compile(r"^\d+\. ")


def strip_num(line):
    return NUM_RE.sub("", line)


def md(text, pclass=""):
    """Markdown-lite: paragraphs, '- ' lists, 'N. ' lists, subheads.

    Subheads inside a slot's body are written '### ' -- '## ' cannot be
    used there, because load_slots() reads any '## ' line as the start of
    a new slot. (The first copyright page hit exactly that: its '###'
    headings were still rendered as literal body text, and '##' would
    instead have split the body into a dozen empty slots.)
    """
    text = re.sub(r"<!--.*?-->", "", text, flags=re.S)
    out = []
    cls = f' class="{pclass}"' if pclass else ""
    for block in re.split(r"\n\s*\n", text.strip()):
        lines = [l.rstrip() for l in block.splitlines() if l.strip()]
        if len(lines) == 1 and lines[0].startswith("### "):
            out.append(f'<h2 class="subhead serif">{inline(lines[0][4:])}</h2>')
        elif len(lines) == 1 and lines[0].startswith("## "):
            out.append(f'<h2 class="subhead serif">{inline(lines[0][3:])}</h2>')
        elif all(l.startswith("> ") for l in lines):
            # Blockquote, added 2026-09-18 for the funding guide: a
            # verbatim quotation of the Secretary's letter has to read
            # as the Department's sentence, not as ours.
            out.append('<blockquote class="pull">'
                       + inline(" ".join(l[2:] for l in lines))
                       + "</blockquote>")
        elif all(l.startswith("- ") or l.startswith("* ") for l in lines):
            items = "".join(f"<li>{inline(l[2:])}</li>" for l in lines)
            out.append(f"<ul>{items}</ul>")
        elif all(re.match(r"^\d+\. ", l) for l in lines):
            items = "".join(f"<li>{inline(strip_num(l))}</li>" for l in lines)
            out.append(f"<ol>{items}</ol>")
        else:
            out.append(f"<p{cls}>{inline(' '.join(lines))}</p>")
    return "\n".join(out)


def rows(slot_text, hcls="svc"):
    """'- **Name.** Body' bullets -> heading/body rows."""
    html = ""
    for l in slot_text.splitlines():
        if not l.startswith("- "):
            continue
        m = re.match(r"- \*\*(.+?)\*\*\s*[—-]?\s*(.*)", l)
        html += f"""<div class="{hcls}"><h3>{inline(m.group(1).rstrip('.'))}</h3>
  <p>{inline(m.group(2))}</p></div>"""
    return html

# ---------------------------------------------------------------- marks

TILE = """<svg class="tile" viewBox="0 0 200 200" width="{w}" height="{w}" xmlns="http://www.w3.org/2000/svg" fill="none" stroke-linecap="round"{extra}>
  <rect x="24" y="24" width="152" height="152" rx="14" stroke="currentColor" stroke-width="6"/>
  <path d="M40 140 C70 110 90 130 110 105 C130 80 150 95 164 78" stroke="currentColor" stroke-width="7"/>
  <path d="M40 118 C68 92 88 110 108 86 C126 65 144 78 160 62" stroke="currentColor" stroke-width="7"/>
  <path d="M40 160 C74 132 96 150 118 126 C136 107 152 116 164 102" stroke="currentColor" stroke-width="7"/>
  <line x1="118" y1="158" x2="160" y2="158" stroke="#e8501e" stroke-width="10"/>
</svg>"""

# Entry curtain (home only): the tile draws itself in, then the curtain
# MELTS under pointer movement — accumulated travel drives fade, blur,
# and sink until it is gone. No cue text, by Joseph's rule. Keyboard or
# click dismisses fully at once; shown once per session.
SPLASH_TILE = """<svg class="splash-tile" viewBox="0 0 200 200" width="180" height="180" xmlns="http://www.w3.org/2000/svg" fill="none" stroke-linecap="round" aria-hidden="true">
  <rect class="d1" x="24" y="24" width="152" height="152" rx="14" stroke="currentColor" stroke-width="4"/>
  <path class="d2" d="M40 118 C68 92 88 110 108 86 C126 65 144 78 160 62" stroke="currentColor" stroke-width="5"/>
  <path class="d3" d="M40 140 C70 110 90 130 110 105 C130 80 150 95 164 78" stroke="currentColor" stroke-width="5"/>
  <path class="d4" d="M40 160 C74 132 96 150 118 126 C136 107 152 116 164 102" stroke="currentColor" stroke-width="5"/>
  <line class="d5" x1="118" y1="158" x2="160" y2="158" stroke="#e8501e" stroke-width="8"/>
</svg>"""

SPLASH_JS = """<script>
(function () {
  var s = document.getElementById('splash');
  if (!s) return;
  try {
    if (sessionStorage.getItem('alcuinSplash')) { s.remove(); return; }
  } catch (e) {}
  document.body.classList.add('locked');
  var armed = false, acc = 0, lx = null, ly = null, done = false;
  setTimeout(function () { armed = true; }, 1600);
  function teardown() {
    window.removeEventListener('mousemove', onMove);
    window.removeEventListener('touchmove', onTouch);
    window.removeEventListener('touchstart', onTouch);
    window.removeEventListener('wheel', onWheel);
    window.removeEventListener('keydown', full);
    window.removeEventListener('click', full);
  }
  function finish() {
    if (done) return;
    done = true;
    document.body.classList.remove('locked');
    try { sessionStorage.setItem('alcuinSplash', '1'); } catch (e) {}
    s.remove();
    teardown();
  }
  function set(p) {
    s.style.setProperty('--p', p);
    if (p >= 1) finish();
  }
  function add(d) {
    if (!armed || done) return;
    acc += d;
    set(Math.min(1, acc / 600));
  }
  function onMove(e) {
    if (lx !== null) add(Math.hypot(e.clientX - lx, e.clientY - ly));
    lx = e.clientX; ly = e.clientY;
  }
  function onTouch(e) {
    var t = e.touches && e.touches[0];
    if (!t) return;
    if (lx !== null) add(Math.hypot(t.clientX - lx, t.clientY - ly) * 2);
    lx = t.clientX; ly = t.clientY;
  }
  function onWheel(e) { add(Math.abs(e.deltaY) + Math.abs(e.deltaX)); }
  function full() { if (armed && !done) set(1); }
  // Auto-lift (2026-09-24): a visitor who sits still no longer faces a
  // dark screen indefinitely. Once the wordmark has risen, the curtain
  // melts on its own from wherever pointer travel left it.
  setTimeout(function () {
    if (done) return;
    var p0 = Math.min(1, acc / 600), t0 = null;
    function step(t) {
      if (done) return;
      if (t0 === null) t0 = t;
      var k = Math.min(1, (t - t0) / 900);
      set(p0 + (1 - p0) * k);
      if (k < 1) requestAnimationFrame(step);
    }
    requestAnimationFrame(step);
  }, 3400);
  window.addEventListener('mousemove', onMove, { passive: true });
  window.addEventListener('touchmove', onTouch, { passive: true });
  window.addEventListener('touchstart', onTouch, { passive: true });
  window.addEventListener('wheel', onWheel, { passive: true });
  window.addEventListener('keydown', full);
  window.addEventListener('click', full);
})();
</script>"""

# Browser-tab icon: the tile mark with fixed brand colors (tokens can't
# reach a favicon). Served as an inline data URI — no extra request.
FAVICON = "data:image/svg+xml," + quote(
    "<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 200 200'>"
    "<rect width='200' height='200' rx='40' fill='#17313b'/>"
    "<g fill='none' stroke='#f6f1e5' stroke-width='12' stroke-linecap='round'>"
    "<path d='M40 140 C70 110 90 130 110 105 C130 80 150 95 164 78'/>"
    "<path d='M40 118 C68 92 88 110 108 86 C126 65 144 78 160 62'/>"
    "<path d='M40 160 C74 132 96 150 118 126 C136 107 152 116 164 102'/>"
    "</g>"
    "<line x1='118' y1='158' x2='160' y2='158' stroke='#e8501e' "
    "stroke-width='16' stroke-linecap='round'/></svg>", safe="")

CONTOURS = """<svg class="contours" viewBox="0 0 1200 260" preserveAspectRatio="xMidYMax slice" xmlns="http://www.w3.org/2000/svg" fill="none" stroke-linecap="round" aria-hidden="true">
  <path d="M-20 220 C180 160 320 230 520 170 C720 110 900 190 1220 120" stroke="currentColor" stroke-width="2" opacity="0.25"/>
  <path d="M-20 250 C200 195 360 255 560 200 C760 145 940 215 1220 155" stroke="currentColor" stroke-width="2" opacity="0.18"/>
</svg>"""

# ---------------------------------------------------------------- css

CSS = """
:root{
  color-scheme:light;
  /* color */
  --teal:#17313b; --teal-deep:#10242c;
  --ember:#e8501e;          /* brand accent: fills, marks, large shapes */
  --ember-strong:#c23c10;   /* orange as text or button ground (AA on cream/white) */
  --ember-dark:#a8360c;     /* hover and press on ember-strong */
  --cream:#f6f1e5; --paper:#fbf8f1; --seafoam:#a9c3c0;
  --surface:#fff; --ink:#1d2a30; --ink-soft:#44565e; --error:#a3341c;
  --line:rgba(23,49,59,.16);        /* decorative rules and dividers */
  --line-strong:rgba(23,49,59,.55); /* borders of interactive elements (3:1) */
  --line-light:rgba(246,241,229,.22);
  --cream-88:rgba(246,241,229,.88);
  --cream-85:rgba(246,241,229,.85);
  --cream-75:rgba(246,241,229,.75);
  /* space scale */
  --s1:4px; --s2:8px; --s3:12px; --s4:16px; --s5:24px; --s6:32px;
  --s7:48px; --s8:64px; --s9:80px;
  /* type scale: 12 14 15 16 18 28 + three clamps */
  --fs-xs:12px; --fs-sm:14px; --fs-md:15px; --fs-base:16px;
  --fs-lg:18px; --fs-sub:28px;
  --fs-h2:clamp(26px,3.4vw,38px);
  --fs-h1-page:clamp(32px,4.5vw,54px);
  --fs-h1-hero:clamp(38px,5.5vw,72px);
}
*{margin:0;padding:0;box-sizing:border-box}
body{background:var(--cream);color:var(--ink);
  font:var(--fs-base)/1.65 Inter,-apple-system,"Helvetica Neue",Arial,sans-serif;
  -webkit-font-smoothing:antialiased}
img{max-width:100%;display:block}
a{color:inherit;text-decoration:none}
::placeholder{color:var(--ink-soft)}
.serif{font-family:"Cormorant Garamond",Georgia,serif}
.wrap{max-width:1140px;margin:0 auto;padding:0 40px}
@media(max-width:720px){.wrap{padding:0 22px}}
@media(prefers-reduced-motion:reduce){
  *,*:before,*:after{transition:none!important;animation:none!important}}

/* utilities (carry what per-page inline styles used to) */
.soft{color:var(--ink-soft)}
.narrow{max-width:38em}
.gap-top{margin-top:var(--s4)}
.gap-top-lg{margin-top:var(--s6)}
.gap-below{margin-bottom:var(--s5)}
.h2-sm{font-size:var(--fs-sub)}
.skip{position:absolute;left:-9999px;top:0;z-index:100;
  background:var(--surface);color:var(--ink);font-weight:600;
  padding:var(--s2) var(--s4);border-radius:0 0 6px 0}
.skip:focus{left:0}

/* labels, buttons */
.kicker{font-size:var(--fs-xs);font-weight:600;letter-spacing:.2em;
  text-transform:uppercase;color:var(--ember-strong)}
.on-dark .kicker{color:var(--seafoam)}
.btn{display:inline-block;background:var(--ember-strong);color:var(--surface);
  font-weight:600;font-size:var(--fs-md);padding:var(--s3) var(--s6);
  border-radius:999px;border:0;cursor:pointer;transition:background .15s}
.btn:hover{background:var(--ember-dark)}
.btn:active{transform:translateY(1px)}
.btn:focus-visible{outline:2px solid var(--ink);outline-offset:2px}
.on-dark .btn:focus-visible,.inquiry .btn:focus-visible,
header .btn:focus-visible{outline-color:var(--cream)}
.btn[disabled]{opacity:.55;cursor:default}
.btn-ghost{display:inline-block;font-weight:600;font-size:var(--fs-md);
  padding:var(--s3) var(--s1)}
.btn-ghost .arr{display:inline-block;transition:transform .15s}
.btn-ghost:hover .arr{transform:translateX(4px)}
.btn-ghost:focus-visible{outline:2px solid var(--cream);outline-offset:2px}
a.more{display:inline-block;font-weight:600;font-size:var(--fs-sm);
  color:var(--ember-strong)}
a.more:hover,a.more:active{color:var(--ember-dark)}
a.more:focus-visible{outline:2px solid var(--ember-strong);outline-offset:2px}

/* header + mobile menu */
header{background:var(--teal);color:var(--cream);position:relative}
.nav{display:flex;align-items:center;gap:30px;padding:var(--s5) 0}
.nav .mark{display:flex;align-items:center;gap:var(--s4);margin-right:auto}
.nav .mark:focus-visible{outline:2px solid var(--seafoam);outline-offset:2px}
.nav .lockup{display:flex;flex-direction:column;line-height:1.2}
.nav .mark .name{font-size:var(--fs-lg);font-weight:600;letter-spacing:.32em}
.nav .mark .proj{font-family:"Cormorant Garamond",Georgia,serif;
  font-style:italic;font-size:var(--fs-lg);color:var(--seafoam);
  align-self:flex-end;margin-right:-.12em}
.nav-links{display:flex;align-items:center;gap:28px}
.nav a.item{font-size:var(--fs-sm);color:var(--cream-85);padding:var(--s1) 0}
.nav a.item:hover,.nav a.item:active{color:var(--surface)}
.nav a.item:focus-visible{outline:2px solid var(--seafoam);outline-offset:2px}
.nav a.item.here{color:var(--surface);border-bottom:2px solid var(--ember)}
.nav .btn{padding:var(--s2) var(--s5);font-size:var(--fs-sm)}
.menu-btn{display:none;background:none;border:1px solid var(--seafoam);
  color:var(--cream);font:600 var(--fs-sm) Inter,sans-serif;
  padding:var(--s2) var(--s4);border-radius:999px;cursor:pointer}
.menu-btn:hover{border-color:var(--cream)}
.menu-btn:focus-visible{outline:2px solid var(--seafoam);outline-offset:2px}
@media(max-width:920px){
  .nav{gap:var(--s4)}
  .nav .mark .name{font-size:var(--fs-base)}
  .nav .mark .proj{font-size:var(--fs-md)}
  .nav .tile{width:44px;height:44px}
  .menu-btn{display:block}
  .nav-links{display:none;position:absolute;left:0;right:0;top:100%;
    background:var(--teal-deep);flex-direction:column;align-items:flex-start;
    gap:0;padding:var(--s2) 22px var(--s5);z-index:40;
    border-top:1px solid var(--line-light)}
  .nav-links.open{display:flex}
  .nav-links a.item{padding:var(--s3) 0;font-size:var(--fs-base);width:100%;
    border-bottom:1px solid var(--line-light)}
  .nav-links a.item.here{color:var(--surface);font-weight:600}
  .nav-links .btn{margin-top:var(--s4)}
}

/* entry curtain (home): melts under pointer movement, no cue text */
body.locked{overflow:hidden}
.splash{position:fixed;inset:0;z-index:60;background:var(--teal);
  color:var(--cream);display:flex;flex-direction:column;align-items:center;
  justify-content:center;gap:var(--s6);--p:0;
  opacity:calc(1 - var(--p));filter:blur(calc(var(--p)*14px))}
.splash .splash-tile{transform:translateY(calc(var(--p)*48px))}
.splash-tile .d1{stroke-dasharray:640;stroke-dashoffset:640;
  animation:draw 1.1s ease-out forwards .2s}
.splash-tile .d2{stroke-dasharray:200;stroke-dashoffset:200;
  animation:draw .8s ease-out forwards 1s}
.splash-tile .d3{stroke-dasharray:200;stroke-dashoffset:200;
  animation:draw .8s ease-out forwards 1.25s}
.splash-tile .d4{stroke-dasharray:200;stroke-dashoffset:200;
  animation:draw .8s ease-out forwards 1.5s}
.splash-tile .d5{stroke-dasharray:60;stroke-dashoffset:60;
  animation:draw .5s ease-out forwards 2.1s}
@keyframes draw{to{stroke-dashoffset:0}}
.splash-word{opacity:0;animation:rise 1s ease forwards 2.3s;
  display:flex;flex-direction:column}
.splash-word .name{font-size:30px;font-weight:600;letter-spacing:.32em}
.splash-word .proj{font-family:"Cormorant Garamond",Georgia,serif;
  font-style:italic;font-size:var(--fs-sub);color:var(--seafoam);
  margin-top:var(--s1);align-self:flex-end;margin-right:-.17em}
@keyframes rise{from{opacity:0;transform:translateY(14px)}
  to{opacity:1;transform:none}}
@media(prefers-reduced-motion:reduce){
  .splash-tile *{stroke-dashoffset:0!important}
  .splash-word{opacity:1}}

/* heroes */
.hero{background:var(--teal);color:var(--cream);padding:var(--s9) 0}
.hero h1{font-family:"Cormorant Garamond",Georgia,serif;font-weight:600;
  font-size:var(--fs-h1-hero);line-height:1.06;margin:var(--s5) 0;
  max-width:12em;text-wrap:balance}
.hero .lede{font-size:var(--fs-lg);line-height:1.7;color:var(--cream-88);
  max-width:33em;margin-bottom:var(--s6);text-wrap:pretty}
.hero-ctas{display:flex;align-items:center;gap:var(--s5);flex-wrap:wrap}
.page-hero{background:var(--teal);color:var(--cream);padding:var(--s7) 0 var(--s8)}
.page-hero h1{font-family:"Cormorant Garamond",Georgia,serif;font-weight:600;
  font-size:var(--fs-h1-page);line-height:1.08;margin:var(--s4) 0;
  text-wrap:balance}
.page-hero .lede{font-size:var(--fs-lg);line-height:1.7;
  color:var(--cream-88);max-width:36em;text-wrap:pretty}
.page-hero .support{display:block;margin-top:var(--s4);font-size:var(--fs-md);
  color:var(--seafoam)}
.page-hero .btn{margin-top:var(--s5)}
@media(max-width:720px){
  .hero{padding:var(--s7) 0 var(--s8)}
  .page-hero{padding:var(--s6) 0 var(--s7)}
}

/* sections */
.section{padding:var(--s9) 0}
.section.tight{padding:var(--s7) 0}
.section.paper{background:var(--paper)}
.section.cream{background:var(--cream)}
.section h2{font-family:"Cormorant Garamond",Georgia,serif;font-weight:600;
  font-size:var(--fs-h2);line-height:1.12;margin:var(--s3) 0 0;
  text-wrap:balance}
.section .intro{font-size:var(--fs-base);line-height:1.7;color:var(--ink-soft);
  max-width:40em;margin-top:var(--s4)}
.subhead{font-family:"Cormorant Garamond",Georgia,serif;font-weight:600;
  font-size:var(--fs-sub);margin:0 0 var(--s4)}
.wrap h2+.prose{margin-top:var(--s4)}
.prose{max-width:42em}
.prose p{margin-bottom:1.3em;line-height:1.75;text-wrap:pretty}
.prose ul,.prose ol{margin:0 0 1.3em 1.2em}
.prose li{margin-bottom:.65em;line-height:1.7}
.prose-narrow{max-width:38em}
.prose-narrow p{font-size:var(--fs-lg);line-height:1.8;margin-bottom:1em;
  text-wrap:pretty}
.prose-narrow .subhead{margin-top:1.6em}
/* guide typography (2026-09-18) ------------------------------------
   The guides were rendering in .prose-narrow, which was written for the
   Our Story essay: 18px, 1.8 leading, no list rules, no link rules.
   That is narrative dress on a reference document. This is their own
   scale -- slightly tighter body, headings that fit the measure and sit
   closer to the text they introduce, real list spacing, and links that
   look like links, which .prose-narrow never gave them. */
.guide-prose{max-width:42em}
.guide-prose p{font-size:17px;line-height:1.72;margin:0 0 1.15em;
  text-wrap:pretty}
/* Headings run to 56 characters ("Ninth through twelfth grade: assess
   independent judgment"). At 29px in a 40em column they could not fit,
   and text-wrap:balance equalised the two lines by breaking mid-phrase
   -- "Kindergarten through third / grade: build the foundations". The
   type is smaller now and the column wider, so the long ones fit on one
   line at desktop; balance is kept for the narrower widths where two
   lines are unavoidable, and text-wrap:pretty on the paragraphs keeps
   single-word orphans off their last lines. */
.guide-prose h2.subhead{font-size:clamp(21px,1.95vw,26px);line-height:1.22;
  margin:2.1em 0 .5em;text-wrap:balance}
.guide-prose h2.subhead:first-child{margin-top:0}
.guide-prose ul,.guide-prose ol{margin:0 0 1.3em 1.15em;padding:0}
.guide-prose li{font-size:17px;line-height:1.7;margin-bottom:.7em;
  padding-left:.2em}
.guide-prose li:last-child{margin-bottom:0}
blockquote.pull{margin:var(--s6) 0;padding:var(--s2) 0 var(--s2) var(--s5);
  border-left:3px solid var(--ember);font-size:var(--fs-lg);line-height:1.6;
  color:var(--ink)}
.guide-prose strong{font-weight:600;color:var(--ink)}
.guide-prose em{color:var(--ink-soft)}
/* Links in running text were indistinguishable from body copy. */
/* Guide CTA on dark (2026-09-18, Joseph's call). The guide page was
   ending on two light bands of similar weight -- CTA then related --
   which read as two endings. Inverting the CTA makes it the dominant
   close and leaves the related band quiet, without moving anything.
   Uses the same teal/cream pair as the site-wide inquiry band. */
.cta-dark{background:var(--teal);color:var(--cream)}
.cta-dark h2{color:var(--cream)}
.cta-dark p{color:var(--cream-85)}

/* related guides (2026-09-18): the library had 8 of 13 guides with no
   inbound sibling links. This band is generated, so it cannot drift
   from the copy and cannot be forgotten on a new guide. */
.rel-grid{display:grid;gap:var(--s4);
  grid-template-columns:repeat(auto-fit,minmax(230px,1fr));
  margin-top:var(--s5)}
.rel-card{display:flex;flex-direction:column;gap:var(--s2);
  background:var(--surface);border:1px solid var(--line);border-radius:2px;
  padding:var(--s5);text-decoration:none}
.rel-card:hover{border-color:var(--ember-strong)}
.rel-card:focus-visible{outline:2px solid var(--ink);outline-offset:2px}
.rel-tag{font:700 var(--fs-xs) Inter,sans-serif;letter-spacing:.05em;
  text-transform:uppercase;color:var(--ember-strong)}
.rel-h{font-weight:600;font-size:var(--fs-base);line-height:1.35;
  color:var(--ink);text-wrap:pretty}
.rel-p{font-size:var(--fs-sm);line-height:1.55;color:var(--ink-soft)}
.prose a:not([class]),.guide-prose a:not([class]){color:var(--ember-strong);
  text-decoration:underline;text-decoration-thickness:1px;
  text-underline-offset:3px;text-decoration-color:rgba(194,60,16,.45)}
.prose a:not([class]):hover,.guide-prose a:not([class]):hover{
  color:var(--ember-dark);text-decoration-color:currentColor}
.prose a:not([class]):focus-visible,
.guide-prose a:not([class]):focus-visible{outline:2px solid var(--ink);
  outline-offset:2px;border-radius:1px}

.rule-sect{border-top:1px solid var(--line);padding-top:var(--s6);
  margin-top:var(--s7)}
.rule-sect h2{margin-bottom:var(--s2)}
.rule-sect .intro{margin-top:var(--s3)}
.byline{font-family:"Cormorant Garamond",Georgia,serif;font-style:italic;
  font-size:var(--fs-lg);color:var(--seafoam);margin-top:var(--s2)}

/* numbered steps */
.steps3{display:grid;grid-template-columns:repeat(3,1fr);gap:var(--s7);
  margin-top:var(--s7);position:relative}
.steps3:before{content:"";position:absolute;top:20px;left:0;right:0;
  height:1px;background:var(--line)}
@media(max-width:920px){.steps3{grid-template-columns:1fr}
  .steps3:before{display:none}}
.step3 .dot{width:40px;height:40px;border-radius:50%;
  border:1px solid var(--ember-strong);background:var(--paper);
  color:var(--ember-strong);font-weight:600;font-size:var(--fs-xs);
  display:flex;align-items:center;justify-content:center;position:relative}
.step3 h3{font-size:var(--fs-base);font-weight:600;margin:var(--s4) 0 var(--s2)}
.step3 p{font-size:var(--fs-md);line-height:1.7;color:var(--ink-soft)}

/* outcome / offering columns */
.cols{display:grid;grid-template-columns:repeat(3,1fr);gap:var(--s7);
  margin-top:var(--s7)}
@media(max-width:920px){.cols{grid-template-columns:1fr;gap:var(--s6)}}
.col{border-top:1px solid var(--line);padding-top:var(--s5);min-width:0}
.col h3{font-size:var(--fs-base);font-weight:600;margin:0 0 var(--s2)}
.col p{font-size:var(--fs-md);line-height:1.7;color:var(--ink-soft)}
.col a.more{margin-top:var(--s4)}

/* service rows */
.svc-grid{display:grid;grid-template-columns:1fr 1fr;gap:0 var(--s7);
  margin-top:var(--s5)}
@media(max-width:920px){.svc-grid{grid-template-columns:1fr}}
.svc{border-top:1px solid var(--line);padding:var(--s5) 0}
.svc h3{font-size:var(--fs-base);font-weight:600;margin-bottom:var(--s2)}
.svc p{font-size:var(--fs-md);line-height:1.7;color:var(--ink-soft)}

/* engagement option rows (training) */
.opt-rows{margin-top:var(--s6);max-width:46em}
.plan-row{display:grid;grid-template-columns:180px 1fr;gap:var(--s5);
  border-top:1px solid var(--line);padding:var(--s4) 0}
@media(max-width:720px){.plan-row{grid-template-columns:1fr;gap:var(--s1)}}
.plan-row .name{font-weight:600;font-size:var(--fs-md)}
.plan-row p{font-size:var(--fs-md);color:var(--ink-soft)}

/* disclosures */
details.disclosure{border:1px solid var(--line);border-radius:6px;
  margin-top:var(--s6);max-width:44em;background:var(--surface)}
details.disclosure summary{cursor:pointer;font-weight:600;
  font-size:var(--fs-md);padding:var(--s4) var(--s5)}
details.disclosure summary:hover{color:var(--ember-strong)}
details.disclosure summary:focus-visible{outline:2px solid var(--ember-strong);
  outline-offset:2px}
details.disclosure .body{padding:0 var(--s5) var(--s4);font-size:var(--fs-md);
  line-height:1.7;color:var(--ink-soft)}
details.disclosure .body p{margin-bottom:.8em}

/* sample standard */
.std-card{background:var(--surface);border:1px solid var(--line);
  border-radius:6px;padding:var(--s6);max-width:46em;margin-top:var(--s6)}
.std-card .meta{font-size:var(--fs-xs);font-weight:600;letter-spacing:.08em;
  text-transform:uppercase;color:var(--ink-soft);margin-bottom:var(--s3)}
.std-card .statement{font-size:var(--fs-base);font-weight:600;
  margin-bottom:var(--s2)}
.std-card .stage{border-top:1px solid var(--line);padding:var(--s3) 0;
  font-size:var(--fs-md);line-height:1.65;color:var(--ink-soft)}
.std-card .stage strong{color:var(--ink)}
.std-card .stages-intro{font-size:var(--fs-sm);color:var(--ink-soft);
  margin:var(--s4) 0 var(--s2)}

/* norms */
.norms{columns:2;column-gap:var(--s7);margin-top:var(--s6);list-style:none;
  counter-reset:norm;max-width:52em}
@media(max-width:720px){.norms{columns:1}}
.norms li{counter-increment:norm;break-inside:avoid;font-size:var(--fs-base);
  padding:var(--s3) 0;border-bottom:1px solid var(--line);text-wrap:pretty}
.norms li:before{content:counter(norm,decimal-leading-zero);
  color:var(--ember-strong);font-weight:600;font-size:var(--fs-xs);
  margin-right:var(--s4)}

/* strands */
.strand-rows{margin-top:var(--s6);max-width:52em}
.strand{display:grid;grid-template-columns:190px 1fr;gap:var(--s5);
  border-top:1px solid var(--line);padding:var(--s4) 0}
@media(max-width:720px){.strand{grid-template-columns:1fr;gap:var(--s1)}}
.strand .name{font-weight:600;font-size:var(--fs-md)}
.strand p{font-size:var(--fs-md);color:var(--ink-soft)}

/* topics (newsletter issues) */
.topics{display:grid;grid-template-columns:repeat(auto-fit,minmax(260px,1fr));
  gap:var(--s6);margin-top:var(--s7)}
.topic{border-top:1px solid var(--line);padding-top:var(--s5)}
.topic h3{font-size:var(--fs-lg);font-weight:600;margin-bottom:var(--s2)}
.topic p{font-size:var(--fs-md);line-height:1.7;color:var(--ink-soft)}

/* founder / about */
.founder{display:flex;align-items:center;gap:var(--s6)}
@media(max-width:720px){.founder{flex-direction:column;
  align-items:flex-start}}
.founder img{width:120px;height:120px;border-radius:50%;object-fit:cover}
.about-grid{display:grid;grid-template-columns:180px 1fr;gap:var(--s7);
  align-items:start}
@media(max-width:720px){.about-grid{grid-template-columns:1fr;gap:var(--s6)}}
.about-grid img{width:180px;height:180px;border-radius:50%;object-fit:cover}

/* inquiry band */
.inquiry{background:var(--teal);color:var(--cream);position:relative;
  overflow:hidden;padding:var(--s9) 0}
.inquiry .contours{position:absolute;right:0;bottom:0;width:70%;
  pointer-events:none;color:var(--seafoam)}
.inquiry .inner{position:relative;max-width:34em}
.inquiry h2{font-family:"Cormorant Garamond",Georgia,serif;font-weight:600;
  font-size:var(--fs-h2);margin-bottom:var(--s4);text-wrap:balance}
.inquiry p{color:var(--cream-85);margin-bottom:var(--s3)}
.inquiry .support{font-size:var(--fs-sm);color:var(--seafoam);
  margin-bottom:var(--s6)}

/* signup */
.signup{background:var(--cream);padding:var(--s7) 0}
.signup h2{font-family:"Cormorant Garamond",Georgia,serif;font-weight:600;
  font-size:var(--fs-h2);margin-bottom:var(--s2)}
.signup p{color:var(--ink-soft);max-width:34em;margin-bottom:var(--s5)}
.signup label{display:block;font-size:var(--fs-sm);font-weight:600;
  margin-bottom:var(--s2)}
.signup form{display:flex;gap:var(--s3);flex-wrap:wrap}
.signup form[hidden]{display:none}
.signup input[aria-invalid="true"]{border-color:var(--error);
  outline:1px solid var(--error)}
.signup input{font:var(--fs-md) Inter,sans-serif;padding:var(--s3) var(--s4);
  border:1px solid var(--line-strong);border-radius:999px;
  background:var(--surface);min-width:min(280px,100%)}
.signup button{font:600 var(--fs-md) Inter,sans-serif;
  padding:var(--s3) var(--s6);border:0;border-radius:999px;
  background:var(--teal);color:var(--cream);cursor:pointer}
.signup button:hover{background:var(--teal-deep)}
.signup button:active{transform:translateY(1px)}
.signup button[disabled]{opacity:.55;cursor:default}
.signup button:focus-visible,.signup input:focus-visible{
  outline:2px solid var(--ember-strong);outline-offset:2px}
.nl-msg{margin-top:var(--s4);font-size:var(--fs-sm);font-weight:600;
  color:var(--ink-soft)}
.nl-msg.error{color:var(--error)}

/* footer */
footer{background:var(--teal-deep);color:var(--cream-75);padding:var(--s7) 0}
.foot-grid{display:grid;grid-template-columns:1.4fr 1fr;gap:var(--s7)}
@media(max-width:720px){.foot-grid{grid-template-columns:1fr;gap:var(--s6)}}
footer .fname{color:var(--cream);font-weight:600;letter-spacing:.22em;
  font-size:var(--fs-xs);margin-bottom:var(--s3)}
footer p{font-size:var(--fs-sm);line-height:1.7;max-width:32em}
footer a{color:var(--cream-85)}
footer a:hover,footer a:active{color:var(--surface)}
footer a:focus-visible{outline:2px solid var(--seafoam);outline-offset:2px}
footer ul{list-style:none;display:flex;flex-wrap:wrap;gap:6px 22px}
footer li{font-size:var(--fs-sm);padding:var(--s1) 0}
.foot-base{border-top:1px solid var(--line-light);margin-top:var(--s7);
  padding-top:var(--s5);font-size:var(--fs-xs);display:flex;
  justify-content:space-between;gap:var(--s4);flex-wrap:wrap}

/* framework downloads */
.dl-list{margin-top:var(--s6);max-width:44em}
a.dl{display:block;background:var(--surface);border:1px solid var(--line-strong);
  border-radius:6px;padding:var(--s4) var(--s5);margin-bottom:var(--s3);
  font-weight:600;font-size:var(--fs-md)}
a.dl svg{color:var(--ember-strong);margin-right:var(--s3);
  vertical-align:-2px}
a.dl:hover{border-color:var(--ember-strong)}
a.dl:active{border-color:var(--ember-dark)}
a.dl:focus-visible{outline:2px solid var(--ember-strong);outline-offset:2px}

/* contact + intake form */
.intake{margin-top:var(--s7);max-width:38em;background:var(--surface);
  border:1px solid var(--line);border-radius:6px;padding:var(--s6)}
.intake .subhead{margin-bottom:var(--s2)}
.field{margin-bottom:var(--s4)}
.field-row{display:grid;grid-template-columns:1fr 1fr;gap:var(--s4)}
@media(max-width:560px){.field-row{grid-template-columns:1fr}}
.field label{display:block;font-size:var(--fs-sm);font-weight:600;
  margin-bottom:var(--s2)}
.field .opt{font-weight:400;color:var(--ink-soft)}
.field input,.field textarea{width:100%;font:var(--fs-md) Inter,sans-serif;
  padding:var(--s3) var(--s4);border:1px solid var(--line-strong);
  border-radius:8px;background:var(--surface)}
.field input:focus-visible,.field textarea:focus-visible{
  outline:2px solid var(--ember-strong);outline-offset:1px}
.field.error input,.field.error textarea{border-color:var(--error);
  outline:1px solid var(--error)}
.field .helper{font-size:var(--fs-xs);color:var(--ink-soft);
  margin-top:var(--s2)}
.form-msg{color:var(--error);font-size:var(--fs-sm);font-weight:600;
  margin:0 0 var(--s4)}
.form-msg a{color:inherit;text-decoration:underline}
.form-msg a:focus-visible,.mail-link:focus-visible{
  outline:2px solid currentColor;outline-offset:2px}
.intake form>.helper{font-size:var(--fs-sm);color:var(--ink-soft);
  margin:0 0 var(--s4)}
.intake .btn{font:600 var(--fs-md) Inter,sans-serif}
.mail-link{font-weight:600;color:var(--ember-strong)}
.mail-link:hover{color:var(--ember-dark)}

/* poster shelf (2026-09-18) --------------------------------------- */
/* The image is never the click target: a .shield sits over every
   poster so "Save image as" and long-press land on an empty div. */
.posters{display:grid;gap:var(--s6);
  grid-template-columns:repeat(auto-fit,minmax(200px,1fr))}
.poster-fig{margin:0}
.poster-shot{position:relative;display:block;width:100%;padding:0;
  border:0;background:none;cursor:zoom-in;line-height:0;
  border-radius:2px;overflow:hidden;
  box-shadow:0 1px 2px rgba(29,42,48,.16),0 10px 24px rgba(29,42,48,.14);
  transition:transform .18s ease,box-shadow .18s ease}
.poster-shot:hover{transform:translateY(-3px);
  box-shadow:0 2px 4px rgba(29,42,48,.18),0 16px 34px rgba(29,42,48,.2)}
.poster-shot:focus-visible{outline:2px solid var(--ink);outline-offset:3px}
.poster-shot img{display:block;width:100%;height:auto;
  -webkit-user-drag:none;user-select:none;-webkit-touch-callout:none}
.shield{position:absolute;inset:0;background:transparent}
.poster-shot .zoom{position:absolute;right:var(--s3);bottom:var(--s3);
  font:600 var(--fs-xs) Inter,sans-serif;letter-spacing:.04em;
  text-transform:uppercase;color:var(--ink);background:var(--cream-88);
  padding:.35em .7em;border-radius:2px;line-height:1.2;
  opacity:0;transition:opacity .18s ease}
.poster-shot:hover .zoom,.poster-shot:focus-visible .zoom{opacity:1}
.poster-fig figcaption{margin-top:var(--s3)}
.poster-fig .pname{font:600 var(--fs-md) Inter,sans-serif;
  letter-spacing:.02em}
.poster-fig p{margin:var(--s1) 0 0;font-size:var(--fs-sm);
  color:var(--ink-soft)}
.buy-rows{display:grid;gap:var(--s3);margin-top:var(--s5)}
.buy-row{display:flex;flex-wrap:wrap;align-items:center;gap:var(--s3);
  justify-content:space-between;padding:var(--s4) var(--s5);
  background:var(--surface);border-radius:2px;
  box-shadow:0 1px 2px rgba(29,42,48,.1)}
.buy-row .what{font:600 var(--fs-md) Inter,sans-serif}
.buy-row .price{font:600 var(--fs-lg) Inter,sans-serif;
  color:var(--ember-strong);margin-left:auto;padding-right:var(--s4)}
@media(max-width:560px){.buy-row .price{margin-left:0;padding-right:0}}
.buy-note{font-size:var(--fs-sm);color:var(--ink-soft);
  margin:var(--s4) 0 0}
/* lightbox */
.lightbox{position:fixed;inset:0;z-index:60;display:none;
  align-items:center;justify-content:center;padding:var(--s5);
  background:rgba(23,49,59,.93)}
.lightbox[open],.lightbox.on{display:flex}
.lightbox figure{margin:0;max-height:100%;display:flex;
  flex-direction:column;align-items:center;gap:var(--s3)}
.lightbox .frame{position:relative;line-height:0;max-height:78vh}
.lightbox img{display:block;max-height:78vh;max-width:100%;
  width:auto;height:auto;-webkit-user-drag:none;user-select:none;
  -webkit-touch-callout:none;box-shadow:0 24px 60px rgba(0,0,0,.45)}
.lightbox figcaption{color:var(--cream);font-size:var(--fs-sm);
  text-align:center;max-width:52ch}
.lightbox .close{position:absolute;top:var(--s4);right:var(--s4);
  font:600 var(--fs-sm) Inter,sans-serif;color:var(--ink);
  background:var(--cream);border:0;border-radius:2px;
  padding:.5em 1em;cursor:pointer}
.lightbox .close:focus-visible{outline:2px solid var(--cream);
  outline-offset:3px}
@media print{.posters,.lightbox{display:none!important}}

/* homepage hero: text left, the three posters right (2026-09-18) --- */
.hero-grid{display:grid;grid-template-columns:minmax(0,1.05fr) minmax(0,.95fr);
  gap:var(--s8);align-items:center}
.hero-copy{min-width:0}
.hero-art{margin:0;min-width:0}
.hero-fan{display:flex;justify-content:center;align-items:flex-end}
.hero-fan img{width:34%;height:auto;display:block;border-radius:1px;
  box-shadow:0 20px 44px rgba(0,0,0,.45);
  border:1px solid rgba(0,0,0,.25)}
.hero-fan .f1{transform:rotate(-7deg) translateX(9%)}
.hero-fan .f3{transform:rotate(7deg) translateX(-9%)}
.hero-fan .f2{position:relative;z-index:2}
.hero-art figcaption{margin-top:var(--s6);text-align:center;
  font-size:var(--fs-sm);color:var(--cream-85);line-height:1.6}
.hero-art figcaption .more{display:inline-block;color:var(--cream)}
.hero-art figcaption .more:hover{color:#fff}
@media(max-width:860px){
  .hero-grid{grid-template-columns:1fr;gap:var(--s7)}
  .hero-fan img{width:29%}
  .hero-art figcaption{text-align:left}}
@media(prefers-reduced-motion:reduce){.hero-fan img{transition:none}}

/* room band (2026-09-18) ------------------------------------------- */
.band{margin:0;position:relative;line-height:0;background:var(--teal)}
.band img{width:100%;height:auto;display:block}
@media(min-width:1100px){
  .band img{max-height:62vh;object-fit:cover;object-position:center 42%}}

/* blog (2026-09-18) ------------------------------------------------ */
.post-list{display:grid;gap:var(--s7)}
/* guides library: chips over one grid (2026-09-18, replaced the rail
   the same day at Joseph's call -- a rail hides most of the library and
   the library is the point). No JS means every card shows, which is the
   correct fallback rather than an empty page. -------------------- */
/* An author display rule beats the UA's [hidden] rule, so .g-card's
   display:flex kept "hidden" cards on screen and the chip filter did
   nothing visible. Checking element.hidden in a console hides this --
   the property is set correctly; only the rendering is wrong. */
[hidden]{display:none!important}
.chips{display:flex;gap:var(--s2);flex-wrap:wrap;margin-bottom:var(--s6);
  padding-bottom:var(--s5);border-bottom:1px solid var(--line)}
.chip{border:1px solid var(--line-strong);background:transparent;
  color:var(--ink);font:600 var(--fs-sm) Inter,sans-serif;padding:7px 15px;
  border-radius:100px;cursor:pointer}
.chip[aria-pressed="true"]{background:var(--teal);border-color:var(--teal);
  color:var(--cream)}
.chip:hover{border-color:var(--teal)}
.chip:focus-visible{outline:2px solid var(--ink);outline-offset:2px}
.chip .n{opacity:.6;font-size:var(--fs-xs);margin-left:4px}
.g-grid{display:grid;gap:var(--s5);
  grid-template-columns:repeat(auto-fill,minmax(280px,1fr))}
.g-card{background:var(--surface);border-radius:2px;padding:var(--s6);
  display:flex;flex-direction:column;
  box-shadow:0 1px 2px rgba(29,42,48,.1),0 8px 20px rgba(29,42,48,.07)}
.g-card h2{font-size:var(--fs-lg);line-height:1.25;margin:0 0 var(--s3)}
.g-card h2 a{color:inherit;text-decoration:none}
.g-card h2 a:hover{color:var(--ember-strong)}
.g-card h2 a:focus-visible{outline:2px solid var(--ink);outline-offset:3px}
.g-card p{margin:0 0 var(--s5);color:var(--ink-soft);
  font-size:var(--fs-sm);line-height:1.65}
.g-card .more{margin-top:auto}
.g-tag{font:600 var(--fs-xs) Inter,sans-serif;letter-spacing:.05em;
  text-transform:uppercase;color:var(--ember-strong);margin:0 0 var(--s2)}
.sr-only{position:absolute;width:1px;height:1px;padding:0;margin:-1px;
  overflow:hidden;clip:rect(0,0,0,0);white-space:nowrap;border:0}
.chip-empty{color:var(--ink-soft);padding:var(--s6) 0}

/* developments board (2026-09-18, replaced the countdown the same day
   at Joseph's call -- a clock only spoke to Utah; a board speaks to
   anyone). Reverse chronological. Every item carries an outbound link
   to the issuing body or a named outlet: an item nobody can go read is
   not worth posting, so the builder drops any row without a url. */
.board-head{display:flex;gap:var(--s4);align-items:baseline;flex-wrap:wrap;
  margin-bottom:var(--s2)}
.board-head h2{margin:0}
.board-note{color:var(--ink-soft);font-size:var(--fs-md);
  margin-bottom:var(--s6);max-width:70ch;text-wrap:pretty}
.board{border-top:2px solid var(--teal);max-width:820px}
.board .item{display:grid;grid-template-columns:132px minmax(0,1fr);
  gap:var(--s5);padding:var(--s5) 0;border-bottom:1px solid var(--line)}
@media(max-width:620px){
  .board .item{grid-template-columns:1fr;gap:var(--s2)}}
.board .d{font-weight:700;font-size:var(--fs-sm);color:var(--teal);
  line-height:1.35}
.board .d small{display:block;font-weight:600;color:var(--ink-soft);
  font-size:var(--fs-xs);margin-top:2px}
.board .w{display:inline-block;font:700 var(--fs-xs) Inter,sans-serif;
  letter-spacing:.05em;text-transform:uppercase;color:var(--ember-strong);
  margin-right:var(--s2)}
.board .h{font-size:var(--fs-base);font-weight:600;margin-bottom:var(--s1);
  line-height:1.4;text-wrap:pretty}
/* text-wrap:pretty keeps a headline from dropping a single word onto
   its own line. Ignored by browsers that do not support it, which is
   why the copy is also written short. */
.board .s{color:var(--ink-soft);font-size:var(--fs-sm);line-height:1.6}
.board .read{display:inline-block;margin-top:var(--s3);
  font:600 var(--fs-sm) Inter,sans-serif;color:var(--ember-strong);
  text-decoration:underline;text-underline-offset:3px}
.board .read:hover{color:var(--ember-dark)}
.board .read .ex{font-size:var(--fs-xs);opacity:.7;margin-left:3px}
.board .read:focus-visible{outline:2px solid var(--ink);outline-offset:2px}
.board .stat{display:block;font-family:"Cormorant Garamond",Georgia,serif;
  font-size:40px;line-height:1;font-weight:600;color:var(--ember-strong);
  margin-bottom:var(--s2)}
.board .item.figure .h{font-size:var(--fs-lg)}
.board .attrib{display:inline-block;margin-top:var(--s3);
  font:600 var(--fs-sm) Inter,sans-serif;color:var(--ink-soft)}
.board .also{display:block;margin-top:var(--s2);font-size:var(--fs-sm)}
.board .also a{color:var(--teal);text-decoration:underline;
  text-underline-offset:3px;font-weight:600}
.board-foot{margin-top:var(--s5);font-size:var(--fs-sm);
  color:var(--ink-soft)}

.guide-card{grid-template-columns:minmax(0,1fr)}
.post-card{display:grid;grid-template-columns:240px minmax(0,1fr);
  gap:var(--s6);align-items:start;max-width:76ch}
.post-card+.post-card{border-top:1px solid var(--line);
  padding-top:var(--s7)}
.card-thumb{display:block;line-height:0;border-radius:2px;overflow:hidden;
  box-shadow:0 1px 3px rgba(29,42,48,.2)}
.card-thumb img{width:100%;height:auto;display:block}
@media(max-width:640px){.post-card{grid-template-columns:1fr;
  gap:var(--s4)}.card-thumb{max-width:340px}}
.post-date,.post-src{font:600 var(--fs-xs) Inter,sans-serif;
  letter-spacing:.06em;text-transform:uppercase;color:var(--ink-soft);
  margin:0 0 var(--s2)}
.post-src{text-transform:none;letter-spacing:.02em;font-weight:400;
  font-size:var(--fs-sm)}
.post-card h2{margin:0 0 var(--s2)}
.post-card h2 a{color:inherit;text-decoration:none}
.post-card h2 a:hover{color:var(--ember-strong)}
.post-card h2 a:focus-visible{outline:2px solid var(--ink);
  outline-offset:3px}
.post-card p{margin:0 0 var(--s3)}
.prose-narrow .post-src{margin-bottom:var(--s5)}
@media(prefers-reduced-motion:reduce){
  .poster-shot,.poster-shot .zoom{transition:none}
  .poster-shot:hover{transform:none}}
"""

CHIPS_JS = """<script>
/* Progressive enhancement: with JS off every card is already visible,
   so this only ever REMOVES cards the reader asked to hide. */
(function(){
  var chips = document.querySelectorAll('.chips .chip');
  if (!chips.length) return;
  var cards = document.querySelectorAll('.g-grid .g-card');
  var empty = document.getElementById('chip-empty');
  chips.forEach(function(chip){
    chip.addEventListener('click', function(){
      var on = chip.getAttribute('aria-pressed') === 'true';
      chips.forEach(function(c){ c.setAttribute('aria-pressed','false'); });
      chip.setAttribute('aria-pressed', on ? 'false' : 'true');
      var want = on ? 'all' : chip.dataset.g;
      var n = 0;
      cards.forEach(function(card){
        var hit = (want === 'all' || card.dataset.g === want);
        card.hidden = !hit; if (hit) n++;
      });
      if (empty) empty.hidden = n > 0;
    });
  });
})();
</script>"""

MENU_JS = """<script>
(function () {
  var btn = document.querySelector('.menu-btn');
  var links = document.querySelector('.nav-links');
  if (!btn || !links) return;
  btn.addEventListener('click', function () {
    var open = links.classList.toggle('open');
    btn.setAttribute('aria-expanded', open ? 'true' : 'false');
    btn.textContent = open ? btn.dataset.close : btn.dataset.open;
  });
})();
</script>"""

# ---------------------------------------------------------------- chrome

G = load_slots("global.md")

NAV_ITEMS = [
    ("Training", "training.html"),
    ("Frameworks", "frameworks.html"),
    ("Guides", "guides.html"),
    ("Blog", "blog.html"),
    ("About", "about.html"),
]


def nav(active, exact=True):
    # exact=False (sub-pages like curriculum.html under Products): no
    # marker at all — a visual .here without aria-current told sighted
    # users they were on Products while telling assistive tech nothing.
    items = ""
    for label, href in NAV_ITEMS:
        here = ' here" aria-current="page' if exact and label == active else ""
        items += f'<a class="item{here}" href="{href}">{label}</a>'
    tile = TILE.format(w=54, extra=' aria-label="The Alcuin Project"')
    cta_current = ""
    return f"""<header><div class="wrap"><nav class="nav">
  <a class="mark" href="index.html">{tile}
    <span class="lockup"><span class="name">ALCUIN</span><span class="proj serif">Project</span></span></a>
  <button class="menu-btn" aria-expanded="false"
    data-open="{esc(G['menu-label'])}" data-close="{esc(G['menu-close-label'])}">{esc(G['menu-label'])}</button>
  <div class="nav-links">{items}
    <a class="btn"{cta_current} href="contact.html">{inline(G['cta-label'])}</a></div>
</nav></div></header>"""


def inquiry_band():
    return f"""<section class="inquiry on-dark"><div class="wrap"><div class="inner">
  <h2>{inline(G['inquiry-heading'])}</h2>
  <p>{inline(G['inquiry-body'])}</p>
  <p class="support">{inline(G['inquiry-support'])}</p>
  <a class="btn" href="contact.html">{inline(G['inquiry-action'])}</a>
</div></div>{CONTOURS}</section>"""


def signup_form(field_id):
    endpoint = G.get("config-signup-endpoint", "").strip()
    # The label lives INSIDE the form so hiding the form on success hides
    # it too (it kept pointing at a hidden input when it sat outside).
    return f"""<form class="nl-form" novalidate data-endpoint="{esc(endpoint)}" data-source="{field_id}">
    <label for="{field_id}">{inline(G['signup-label'])}</label>
    <input id="{field_id}" type="email" name="email" required
    autocomplete="email" placeholder="{esc(G['signup-placeholder'])}">
    <button type="submit">{inline(G['signup-action'])}</button></form>
  <p class="nl-msg" role="status" tabindex="-1" hidden></p>"""


def signup_js():
    # One newsletter list (decision 2026-09-10), separate from booking
    # intake. Endpoint lives in copy/global.md ## config-signup-endpoint;
    # server code: booking/newsletter_apps_script.gs.
    return rf"""<script>
(function () {{
  var form = document.querySelector('.nl-form');
  if (!form) return;
  var msg = form.parentElement.querySelector('.nl-msg');
  var btn = form.querySelector('button');
  var input = form.querySelector('input');
  var ENDPOINT = form.dataset.endpoint;
  function show(text, isError) {{
    msg.textContent = text; msg.hidden = false;
    msg.classList.toggle('error', !!isError);
  }}
  form.addEventListener('submit', function (ev) {{
    ev.preventDefault();
    msg.hidden = true;
    var email = input.value.trim();
    var bad = !/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(email);
    input.setAttribute('aria-invalid', bad ? 'true' : 'false');
    if (bad) {{ show({G['signup-msg-invalid']!r}, true); input.focus(); return; }}
    if (!ENDPOINT) {{ show({G['signup-msg-error']!r}, true); return; }}
    var label = btn.textContent;
    btn.disabled = true;
    btn.textContent = {G['signup-msg-sending']!r};
    var id = (window.crypto && crypto.randomUUID) ? crypto.randomUUID()
             : String(Date.now()) + '-' + Math.random().toString(16).slice(2);
    fetch(ENDPOINT, {{ method: 'POST',
        headers: {{ 'Content-Type': 'text/plain;charset=utf-8' }},
        body: JSON.stringify({{ id: id, email: email,
          source: form.dataset.source }}) }})
      .then(function (r) {{ return r.json(); }})
      .then(function (res) {{
        if (res && res.ok) {{
          form.hidden = true;
          show({G['signup-msg-success']!r}, false);
          msg.focus({{ preventScroll: true }});
        }}
        else {{ show({G['signup-msg-error']!r}, true); }}
      }})
      .catch(function () {{ show({G['signup-msg-error']!r}, true); }})
      .finally(function () {{ btn.disabled = false; btn.textContent = label; }});
  }});
}})();
</script>"""


def signup_band(field_id="nl-email", heading=None, body=None):
    return f"""<section class="signup"><div class="wrap">
  <h2>{inline(heading or G['signup-heading'])}</h2>
  <p>{inline(body or G['signup-body'])}</p>
  {signup_form(field_id)}
</div></section>"""


def footer():
    links = "".join(f'<li><a href="{href}">{label}</a></li>'
                    for label, href in NAV_ITEMS + [
                        ("Our story", "our-story.html"),
                        ("Privacy", "privacy.html"),
                        ("Copyright", "copyright.html"),
                        ("Book a call", "contact.html")])
    return f"""<footer><div class="wrap">
<div class="foot-grid">
  <div><div class="fname">{esc(G['footer-name']).upper()}</div>
    <p>{inline(G['footer-body'])}</p></div>
  <div><ul>{links}</ul></div>
</div>
<div class="foot-base"><span><a href="copyright.html">{inline(G['footer-copyright'])}</a></span>
  <a href="mailto:{G['footer-contact']}">{inline(G['footer-contact'])}</a></div>
</div></footer>"""


DEFAULT_SHARE_IMAGE = "assets/classroom-1400.jpg"
# Replaced with the real absolute URL in main(), where the filename is
# known. page() itself has no idea what it is being written as.
CANON_TOKEN = "@@CANONICAL@@"


def trim_desc(text, limit=155):
    """Meta descriptions are cut around 155 characters; cut on a word."""
    text = " ".join(text.split())
    if len(text) <= limit:
        return text
    cut = text[:limit].rsplit(" ", 1)[0].rstrip(",;:-—– ")
    return cut + "…"


def share_tags(slots):
    """Canonical URL and Open Graph tags. Every page gets both.

    A blog post supplies its own lead card as share-image; everything
    else falls back to the classroom photograph, so a link pasted into
    Slack or a text message never unfurls bare.
    """
    img = slots.get("share-image", DEFAULT_SHARE_IMAGE)
    kind = "article" if slots.get("share-image") else "website"
    title = esc(slots.get("share-title", slots["browser-title"]))
    canon = CANON_TOKEN
    return "\n".join([
        f'<link rel="canonical" href="{canon}">',
        f'<meta property="og:type" content="{kind}">',
        f'<meta property="og:url" content="{canon}">',
        f'<meta property="og:site_name" content="The Alcuin Project">',
        f'<meta property="og:title" content="{title}">',
        f'<meta property="og:description" '
        f'content="{esc(slots["meta-description"])}">',
        f'<meta property="og:image" content="{SITE_URL}/{img}">',
        f'<meta name="twitter:card" content="summary_large_image">',
    ])


def org_jsonld():
    """Organization data for the homepage. Tells a search engine what
    kind of thing this is, which the page text alone does not."""
    import json
    data = {
        "@context": "https://schema.org",
        "@type": "Organization",
        "name": "The Alcuin Project",
        "url": SITE_URL + "/",
        "logo": f"{SITE_URL}/{DEFAULT_SHARE_IMAGE}",
        "description": "AI training and coaching for K-12 schools, using "
                       "teachers' own lessons and materials.",
        "email": G["footer-contact"],
        "areaServed": "US",
        "knowsAbout": ["AI literacy", "professional development",
                       "curriculum design", "K-12 education"],
        "sameAs": [],
    }
    return ('<script type="application/ld+json">'
            + json.dumps(data, separators=(",", ":")) + "</script>")


def page(slots, active, body, ending="inquiry", exact=True):
    end = inquiry_band() if ending == "inquiry" else ""
    robots = ('<meta name="robots" content="noindex">\n'
              if PRELAUNCH or slots.get("force-noindex") else "")
    nl_js = signup_js() if 'class="nl-form"' in body else ""
    chip_js = CHIPS_JS if 'class="chips"' in body else ""
    return f"""<!doctype html>
<html lang="en"><head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
{robots}<meta name="description" content="{esc(slots['meta-description'])}">
{share_tags(slots)}
{org_jsonld() if slots.get('jsonld') else ''}{slots.get('extra-jsonld','')}
<title>{esc(slots['browser-title'])}</title>
<link rel="icon" href="{FAVICON}">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,600;1,500&family=Inter:wght@400;600&display=swap" rel="stylesheet">
<style>{CSS}</style>
</head><body>
<a class="skip" href="#main">Skip to content</a>
{nav(active, exact)}
<main id="main">
{body}
{end}
</main>
{footer()}
{MENU_JS}
{chip_js}
{nl_js}
</body></html>"""

# ---------------------------------------------------------------- home

def build_home():
    H = load_slots("home.md")
    splash = f"""<div class="splash" id="splash" aria-hidden="true">
  {SPLASH_TILE}
  <div class="splash-word"><div class="name">ALCUIN</div>
    <div class="proj">Project</div></div>
</div>
{SPLASH_JS}"""

    # 2026-09-18, review finding (high): the hero text sat left with the
    # artwork centred beneath it, leaving the right half of the band
    # empty on desktop. The band is now two columns -- text left, the
    # three posters right -- and stacks on narrow screens. Joseph's
    # choice of all three designs (Hero C) is kept; only the placement
    # changed, from under the text to beside it.
    #
    # Review finding (medium): the artwork had no next step. It links to
    # the posters on Products. The caption that briefly sat above that
    # link is cut (Joseph, 2026-09-18); posters-caption stays in
    # home.md, unrendered.
    fan = "".join(
        f'<img class="f{i}" src="assets/poster-{slug}-thumb.jpg" alt=""'
        f' width="667" height="1000" loading="lazy" decoding="async">'
        for i, (slug, _f) in enumerate(POSTERS, 1))

    hero = f"""<section class="hero on-dark"><div class="wrap">
  <div class="hero-grid">
    <div class="hero-copy">
      <div class="kicker">{inline(H['hero-eyebrow'])}</div>
      <h1>{inline(H['hero-h1'])}</h1>
      <p class="lede">{inline(H['hero-body'])}</p>
      <div class="hero-ctas">
        <a class="btn" href="training.html">{inline(H['hero-primary'])}</a>
        <a class="btn-ghost" href="contact.html">{inline(H['hero-secondary'])} <span class="arr">&rarr;</span></a>
      </div>
    </div>
    <figure class="hero-art">
      <div class="hero-fan">{fan}</div>
      <figcaption></figcaption>
    </figure>
  </div>
</div></section>"""

    # 2026-09-10 merge (approved): the "Work with Alcuin" grid is gone;
    # its technology-solutions card lives here and its curriculum card
    # lives in the outcomes section. offering-1/offering-3 card texts and
    # the offerings-heading slot are retired (still in home.md, unused).
    # 2026-09-18 (Joseph): "Start with a lesson you're already teaching"
    # and "What should students do for themselves?" cut from the landing
    # page; work-* and principle-* slots retired (still in home.md,
    # unused; both blocks still live on training.html / why-alcuin.html).
    # Technology solutions was NOT cut -- it was nested inside the work
    # section, so it is promoted to a section of its own here.
    tech = f"""<section class="section paper"><div class="wrap">
  <h2>{inline(H['offering-2-heading'])}</h2>
  <div class="prose"><p>{inline(H['offering-2-body'])}</p></div>
</div></section>"""

    out_cols = "".join(f"""<div class="col">
  <h3>{inline(H[f'outcome-{i}-heading'])}</h3>
  <p>{inline(H[f'outcome-{i}-body'])}</p></div>""" for i in (1, 2, 3))
    outcomes = f"""<section class="section cream"><div class="wrap">
  <h2>{inline(H['outcomes-heading'])}</h2>
  <p class="intro">{inline(H['outcomes-intro'])}</p>
  <div class="cols">{out_cols}</div>
  <a class="more gap-top-lg" href="frameworks.html">{inline(H['outcomes-action'])} &rarr;</a>
  <div class="rule-sect">
    <h2 class="subhead serif">{inline(H['offering-4-heading'])}</h2>
    <div class="prose"><p>{inline(H['offering-4-body'])}</p></div>
    <a class="more" href="curriculum.html">{inline(H['offering-4-action'])} &rarr;</a>
  </div>
</div></section>"""

    # 2026-09-18 (Joseph): "Meet Joseph Dockstader" cut from the landing
    # page; it stays on about.html. founder-* slots retired in home.md.

    # 2026-09-18, review finding (medium): Technology solutions was the
    # first section under a hero that promotes training, which gave the
    # secondary service top billing. The learning framework now comes
    # first and technology follows it.
    # 2026-09-18 (Joseph): the room photograph, full bleed, between the
    # framework and technology sections -- it breaks the run of text
    # blocks the review flagged, and shows the poster in a room rather
    # than on a white page. Sizes are generated by build_classroom();
    # the widest is the source's own width, since nothing is upscaled.
    room = ""
    if CLASSROOM.exists():
        widths = [w for w in CLASSROOM_WIDTHS if w <= Image.open(
            CLASSROOM).width]
        srcset = ", ".join(f"assets/classroom-{w}.jpg {w}w" for w in widths)
        room = f"""<figure class="band">
  <img src="assets/classroom-{widths[-1]}.jpg" srcset="{srcset}"
    sizes="100vw" alt="{esc(H['room-alt'])}"
    loading="lazy" decoding="async">
</figure>"""

    # 2026-09-24: entry curtain taken off at Joseph's call; analytics showed
    # visitors were not getting past the home page. Markup and JS stay above;
    # set SHOW_SPLASH = True to bring it back.
    body = (splash if SHOW_SPLASH else "") + hero + outcomes + room + tech
    H["jsonld"] = "1"
    return page(H, "", body)

# ---------------------------------------------------------------- training

def build_training():
    T = load_slots("training.md")
    hero = f"""<section class="page-hero on-dark"><div class="wrap">
  <h1>{inline(T['hero-h1'])}</h1>
  <p class="lede">{inline(T['hero-body'])}</p>
  <a class="btn" href="contact.html">{inline(T['hero-action'])}</a>
</div></section>"""

    steps = "".join(f"""<div class="step3"><div class="dot">{i}</div>
  <h3>{inline(T[f'step-{i}-heading'])}</h3>
  <p>{inline(T[f'step-{i}-body'])}</p></div>""" for i in (1, 2, 3))
    sequence = f"""<section class="section paper"><div class="wrap">
  <h2>{inline(T['sequence-heading'])}</h2>
  <p class="intro">{inline(T['sequence-intro'])}</p>
  <div class="steps3">{steps}</div>
</div></section>"""

    services = f"""<section class="section cream"><div class="wrap">
  <h2>{inline(T['services-heading'])}</h2>
  <div class="svc-grid">{rows(T['services'])}</div>
</div></section>"""
    # 2026-09-18 (Joseph): "Technology solutions" moved to products.html
    # (copy moved to copy/products.md); "Support for school decisions"
    # cut from this page -- advisory-* slots kept in copy/training.md,
    # unrendered, pending a decision on where that section belongs.

    opts = ""
    for l in T["options"].splitlines():
        m = re.match(r"- \*\*(.+?)\*\*\s*—\s*(.*)", l)
        if m:
            opts += f"""<div class="plan-row"><div class="name">{inline(m.group(1))}</div>
  <p>{inline(m.group(2))}</p></div>"""
    options = f"""<section class="section paper"><div class="wrap">
  <h2>{inline(T['options-heading'])}</h2>
  <div class="opt-rows">{opts}</div>
  <div class="prose gap-top-lg">
    <p>{inline(T['options-note'])}</p>
    <p>{inline(T['pricing-line'])}</p></div>
</div></section>"""

    prep = f"""<section class="section tight cream"><div class="wrap">
  <h2>{inline(T['prep-heading'])}</h2>
  <div class="prose">{md(T['prep-body'])}</div>
</div></section>"""

    body = hero + sequence + services + options + prep
    return page(T, "Training", body)

# ---------------------------------------------------------------- frameworks

def build_frameworks():
    F = load_slots("frameworks.md")
    hero = f"""<section class="page-hero on-dark"><div class="wrap">
  <div class="kicker">{inline(F['hero-eyebrow'])}</div>
  <h1>{inline(F['hero-h1'])}</h1>
  <p class="lede">{inline(F['hero-body'])}</p>
</div></section>"""

    purpose = f"""<section class="section paper"><div class="wrap">
  <h2>{inline(F['purpose-heading'])}</h2>
  <div class="prose">{md(F['purpose-body'])}</div>
  <details class="disclosure"><summary>{inline(F['publication-label'])}</summary>
    <div class="body">{md(F['publication-notes'])}</div></details>
</div></section>"""

    dl_icon = ('<svg viewBox="0 0 16 16" width="15" height="15" aria-hidden="true" '
               'fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round">'
               '<path d="M8 2v8M4.5 7 8 10.5 11.5 7M3 13.5h10"/></svg>')
    downloads = f"""<section class="section tight cream"><div class="wrap">
  <h2>{inline(F['downloads-heading'])}</h2>
  <div class="dl-list">
    <a class="dl" href="assets/alcuin-ai-literacy-framework.pdf" download="Alcuin_AI_Literacy_Framework.pdf">{dl_icon}{inline(F['download-framework-label'])}</a>
    <a class="dl" href="assets/alcuin-ai-literacy-standards.pdf" download="Alcuin_AI_Literacy_Standards.pdf">{dl_icon}{inline(F['download-curriculum-label'])}</a>
  </div>
</div></section>"""

    strand_rows = ""
    for l in F["strands"].splitlines():
        m = re.match(r"- \*\*(.+?)\*\*\s*—\s*(.*)", l)
        if m:
            strand_rows += f"""<div class="strand"><div class="name">{inline(m.group(1))}</div>
  <p>{inline(m.group(2))}</p></div>"""
    strands = f"""<section class="section cream"><div class="wrap">
  <h2>{inline(F['strands-heading'])}</h2>
  <p class="intro">{inline(F['strands-intro'])}</p>
  <div class="strand-rows">{strand_rows}</div>
</div></section>"""

    stages = "".join(f'<div class="stage">{inline(F[f"sample-stage-{i}"])}</div>'
                     for i in (1, 2, 3, 4))
    sample = f"""<section class="section paper"><div class="wrap">
  <div class="kicker">{inline(F['sample-eyebrow'])}</div>
  <h2>{inline(F['sample-heading'])}</h2>
  <div class="std-card">
    <div class="meta">{inline(F['sample-meta'])}</div>
    <p class="statement">{inline(F['sample-statement'])}</p>
    <p class="stages-intro">{inline(F['sample-intro'])}</p>
    {stages}
  </div>
  <details class="disclosure"><summary>{inline(F['crosswalk-label'])}</summary>
    <div class="body">{md(F['crosswalk-notes'])}</div></details>
</div></section>"""

    norms_html = "".join(
        f"<li>{inline(strip_num(l)).replace('on it.', 'on&nbsp;it.')}</li>"
        for l in F["norms"].splitlines() if l.strip())
    norms = f"""<section class="section cream"><div class="wrap">
  <h2>{inline(F['norms-heading'])}</h2>
  <p class="intro">{inline(F['norms-intro'])}</p>
  <ol class="norms">{norms_html}</ol>
</div></section>"""

    closing = f"""<section class="section tight paper"><div class="wrap">
  <h2>{inline(F['closing-heading'])}</h2>
  <p class="intro">{inline(F['closing-body'])}</p>
  <div class="hero-ctas gap-top-lg">
    <a class="btn" href="contact.html">{inline(F['closing-primary'])}</a></div>
</div></section>"""

    body = hero + purpose + downloads + strands + sample + norms + closing
    return page(F, "Frameworks", body, ending="none")

# ---------------------------------------------------------------- products

def build_products():
    P = load_slots("products.md")
    hero = f"""<section class="page-hero on-dark"><div class="wrap">
  <div class="kicker">{inline(P['hero-eyebrow'])}</div>
  <h1>{inline(P['hero-h1'])}</h1>
  <p class="lede">{inline(P['hero-body'])}</p>
</div></section>"""

    # 2026-09-18 (Joseph): "The Teacher-Room Set" cut from the page for
    # now -- first-heading/first-body stay in products.md, unrendered.

    rel = ""
    dests = {"related-1": "poster-curriculum.html",
             "related-2": "curriculum.html",
             "related-3": "#technology"}
    for key, dest in dests.items():
        rel += f"""<div class="col"><h3>{inline(P[f'{key}-heading'])}</h3>
  <p>{inline(P[f'{key}-body'])}</p>
  <a class="more" href="{dest}">{inline(P[f'{key}-action'])} &rarr;</a></div>"""
    related = f"""<section class="section cream"><div class="wrap">
  <h2>{inline(P['related-heading'])}</h2>
  <div class="cols">{rel}</div>
</div></section>"""

    # 2026-09-18 (Joseph): "Technology solutions" moved here from
    # training.html; the related-3 "Tools and apps" card now links to it
    # on this page, and home.html points at products.html#technology.
    tech = f"""<section class="section paper" id="technology"><div class="wrap">
  <h2>{inline(P['tech-heading'])}</h2>
  <p class="intro">{inline(P['tech-intro'])}</p>
  <div class="svc-grid">{rows(P['tech'])}</div>
</div></section>"""

    # 2026-09-18 (Joseph): Products is HIDDEN until the way the posters are
# sold is decided. build_products() and build_poster_curriculum() are
# kept and still work; they are simply not registered in main(), so no
# page is written and nothing links to them. poster-curriculum went with
# it because Products was its only route in -- an orphan page nobody can
# reach is worse than no page. To bring them back: re-add both to the
# pages dict, put ("Products", "products.html") back in NAV_ITEMS, and
# restore the two homepage links and curriculum's closing link.
#
# 2026-09-18 (Joseph): the AI Norms poster shelf.
    #
    # On "cannot be downloaded and plagiarized": a browser cannot be made
    # to withhold an image it has displayed, and no markup stops a
    # screenshot. What is done here instead:
    #   - only DERIVED files are published (440px/1100px JPEGs, roughly
    #     12-30 DPI at 24x36 -- unusable as a print);
    #   - the watermark is burned into the pixels, not laid over them in
    #     CSS, so a saved or screenshotted copy carries it;
    #   - the print PDFs are never published to the site at all;
    #   - right-click, drag and long-press are blocked, and a .shield div
    #     covers each image so "Save image as" has no image to target.
    # That is deterrence against casual copying. The real protection is
    # the copyright terms on copyright.html.
    shots = ""
    for i, (slug, _f) in enumerate(POSTERS, 1):
        name = esc(P[f'poster-{i}-name'])
        shots += f"""<figure class="poster-fig">
  <button class="poster-shot" type="button" data-poster="{slug}"
    data-name="{name}" aria-label="Preview the {name} poster, larger">
    <img src="assets/poster-{slug}-thumb.jpg" alt="{name} poster design"
      width="667" height="1000" loading="lazy" decoding="async" draggable="false">
    <span class="shield"></span><span class="zoom">Preview</span>
  </button>
  <figcaption><div class="pname">{inline(P[f'poster-{i}-name'])}</div></figcaption>
</figure>"""

    # Note (not shipped to the page, deliberately): the previews are
    # downscaled and carry a burned-in watermark, and the shield/context
    # -menu handlers block the casual save routes. The site does not say
    # any of that -- Joseph's call 2026-09-18: keep the watermark, don't
    # announce it.
    #
    # 2026-09-18 (Joseph, third pass): the section is the heading and the
    # three named thumbnails. Everything else is cut -- posters-intro,
    # the per-poster descriptions, the size/printing spec, the
    # single/set buy rows and their note, the pre-launch status line, and
    # the "previews are watermarked" line (the watermark stays; naming it
    # does not). All those slots remain in products.md, unrendered.
    posters = f"""<section class="section cream" id="posters"><div class="wrap">
  <h2>{inline(P['posters-heading'])}</h2>
  <div class="posters gap-top-lg">{shots}</div>
</div></section>
<div class="lightbox" id="lightbox" role="dialog" aria-modal="true"
  aria-label="Poster preview" hidden>
  <button class="close" type="button" id="lb-close">Close</button>
  <figure>
    <div class="frame">
      <img id="lb-img" src="" alt="" draggable="false">
      <span class="shield"></span>
    </div>
    <figcaption id="lb-cap"></figcaption>
  </figure>
</div>
<script>
(function () {{
  var box = document.getElementById('lightbox');
  var img = document.getElementById('lb-img');
  var cap = document.getElementById('lb-cap');
  var shut = document.getElementById('lb-close');
  var last = null;
  if (!box) return;
  document.addEventListener('contextmenu', function (ev) {{
    if (ev.target.closest('.poster-shot, .lightbox')) ev.preventDefault();
  }});
  document.addEventListener('dragstart', function (ev) {{
    if (ev.target.closest('.poster-shot, .lightbox')) ev.preventDefault();
  }});
  function open(btn) {{
    last = btn;
    img.src = 'assets/poster-' + btn.dataset.poster + '-preview.jpg';
    img.alt = btn.dataset.name + ' poster design, enlarged preview';
    cap.textContent = btn.dataset.name;
    box.hidden = false; box.classList.add('on');
    document.body.style.overflow = 'hidden';
    shut.focus();
  }}
  function close() {{
    box.classList.remove('on'); box.hidden = true;
    document.body.style.overflow = '';
    img.src = '';
    if (last) last.focus();
  }}
  Array.prototype.forEach.call(
    document.querySelectorAll('.poster-shot'), function (b) {{
      b.addEventListener('click', function () {{ open(b); }});
    }});
  shut.addEventListener('click', close);
  box.addEventListener('click', function (ev) {{
    if (!ev.target.closest('figure')) close();
  }});
  document.addEventListener('keydown', function (ev) {{
    if (box.hidden) return;
    if (ev.key === 'Escape') {{ close(); return; }}
    if (ev.key === 'Tab') {{ ev.preventDefault(); shut.focus(); }}
  }});
}})();
</script>"""

    closing = signup_band("nl-email-products", P["closing-heading"],
                          P["closing-body"])
    body = hero + posters + related + tech + closing
    return page(P, "Products", body, ending="none")


def build_curriculum():
    C = load_slots("curriculum.md")
    hero = f"""<section class="page-hero on-dark"><div class="wrap">
  <div class="kicker">{inline(C['hero-eyebrow'])}</div>
  <h1>{inline(C['hero-h1'])}</h1>
  <p class="lede">{inline(C['hero-body'])}</p>
</div></section>"""
    scope = f"""<section class="section paper"><div class="wrap">
  <h2>{inline(C['scope-heading'])}</h2>
  <div class="prose">{md(C['scope-body'])}</div>
</div></section>"""
    closing = signup_band("nl-email-curr", C["closing-heading"])
    return page(C, "", hero + scope + closing, ending="none",
                exact=False)


def build_poster_curriculum():
    P = load_slots("poster_curriculum.md")
    hero = f"""<section class="page-hero on-dark"><div class="wrap">
  <div class="kicker">{inline(P['hero-eyebrow'])}</div>
  <h1>{inline(P['hero-h1'])}</h1>
  <p class="lede">{inline(P['hero-body'])}</p>
</div></section>"""
    avail = f"""<section class="section paper"><div class="wrap">
  <h2>{inline(P['availability-heading'])}</h2>
  <div class="prose"><p>{inline(P['availability-body'])}</p></div>
</div></section>"""
    closing = signup_band("nl-email-poster", P["closing-heading"]) + f"""
<section class="section tight cream"><div class="wrap">
  <a class="more" href="products.html">{inline(P['closing-link'])} &rarr;</a>
</div></section>"""
    return page(P, "Products", hero + avail + closing, ending="none",
                exact=False)

# ---------------------------------------------------------------- newsletter

# 2026-09-18 (Joseph): the newsletter page becomes a blog. Posts are
# files in copy/posts/ -- see the README there. The email signup is kept,
# at the foot of the index, so the page reads before it asks.
#
# build_newsletter() is gone; copy/newsletter.md is retained, unused.

def load_posts():
    """Every copy/posts/*.md as (slug, slots), newest date first."""
    out = []
    folder = COPY / "posts"
    if not folder.is_dir():
        return out
    for f in sorted(folder.glob("*.md")):
        if f.name == "README.md":
            continue
        slots = load_slots(f"posts/{f.name}")
        missing = [k for k in ("title", "date", "summary", "body")
                   if not slots.get(k)]
        if missing:
            print(f"  ! skipping posts/{f.name}: no {', '.join(missing)}")
            continue
        out.append((f.stem, slots))
    out.sort(key=lambda kv: kv[1]["date"], reverse=True)
    return out


def post_page_name(slug):
    return f"blog-{slug}.html"


def pretty_date(iso):
    try:
        return datetime.date.fromisoformat(iso.strip()).strftime(
            "%B %-d, %Y")
    except ValueError:
        return iso.strip()


def source_line(P, B):
    """Credit line for a post about someone else's article."""
    if not P.get("link-url"):
        return ""
    who = esc(P.get("link-source", "").strip())
    by = esc(P.get("link-author", "").strip())
    if by and who:
        who = f"{by}, {who}"
    elif by:
        who = by
    return f'<p class="post-src">{who}</p>' if who else ""


def build_blog():
    B = load_slots("blog.md")
    posts = load_posts()
    hero = f"""<section class="page-hero on-dark"><div class="wrap">
  <h1>{inline(B['hero-h1'])}</h1>
  <p class="lede">{inline(B['hero-body'])}</p>
</div></section>"""

    if posts:
        items = ""
        for slug, P in posts:
            items += f"""<article class="post-card">
  <a class="card-thumb" href="{post_page_name(slug)}" tabindex="-1" aria-hidden="true">
    <img src="assets/card-{slug}.jpg" alt="" width="1200" height="630"
      loading="lazy" decoding="async"></a>
  <div>
    <p class="post-date">{esc(pretty_date(P['date']))}</p>
    <h2><a href="{post_page_name(slug)}">{inline(P['title'])}</a></h2>
    {source_line(P, B)}
    <p>{inline(P['summary'])}</p>
    <a class="more" href="{post_page_name(slug)}">{inline(B['read-more'])} &rarr;</a>
  </div>
</article>"""
        listing = f"""<section class="section paper"><div class="wrap">
  <div class="post-list">{items}</div>
</div></section>"""
    else:
        listing = f"""<section class="section paper"><div class="wrap">
  <p class="intro">{inline(B['empty-note'])}</p>
</div></section>"""

    signup = signup_band("nl-email", B["signup-heading"], B["signup-body"])
    return page(B, "Blog", hero + listing + signup, ending="none")


def build_post(slug, P, B):
    src = ""
    if P.get("link-url"):
        who = P.get("link-source", "").strip() or "the original"
        src = f"""<div class="rule-sect narrow">
  <a class="more" href="{esc(P['link-url'].strip())}"
    target="_blank" rel="noopener noreferrer">{inline(B['link-out-label'])}
    at {esc(who)} &rarr;</a>
</div>"""
    hero = f"""<section class="page-hero on-dark"><div class="wrap">
  <p class="byline">{esc(pretty_date(P['date']))}</p>
  <h1>{inline(P['title'])}</h1>
</div></section>"""
    body = f"""<section class="section paper"><div class="wrap">
  <div class="prose-narrow">{source_line(P, B)}
    {md(P['body'])}</div>
  {src}
  <div class="rule-sect narrow">
    <a class="more" href="blog.html">&larr; All posts</a></div>
</div></section>"""
    # A search result truncates around 60 characters, so the brand suffix
    # is dropped rather than the headline when both will not fit.
    full = f"{P['title']} | The Alcuin Project"
    slots = {"browser-title": full if len(full) <= 60 else P["title"],
             "meta-description": trim_desc(P["summary"]),
             "share-image": f"assets/card-{slug}.jpg",
             "share-title": P["title"]}
    return page(slots, "Blog", hero + body, ending="none")

# ---------------------------------------------------------------- about# ---------------------------------------------------------------- about

# 2026-09-18 (Joseph): About is now the company page. The Vision,
# Mission and core values moved here from why-alcuin.html, which is cut;
# "Meet the founder" is demoted from the page title to a section below
# them, on the small .founder portrait rather than the 180px about-grid.
# hero-name is retired (still in about.md, unused).
#
# 2026-09-18 (Joseph), second pass: values-intro ("Seven, sequenced from
# the handshake to the child") and the whole "Keep the learning goal in
# view" section are cut. Both slots stay in about.md, unrendered.
def build_about():
    A = load_slots("about.md")
    hero = f"""<section class="page-hero on-dark"><div class="wrap">
  <h1>{inline(A['hero-h1'])}</h1>
  <p class="lede">{inline(A['hero-body'])}</p>
</div></section>"""

    purpose = f"""<section class="section paper"><div class="wrap">
  <h2>{inline(A['vision-heading'])}</h2>
  <div class="prose"><p class="intro">{inline(A['vision-body'])}</p></div>
  <div class="rule-sect"><h2>{inline(A['mission-heading'])}</h2>
    <div class="prose"><p class="intro">{inline(A['mission-body'])}</p></div></div>
</div></section>"""

    values = f"""<section class="section cream"><div class="wrap">
  <h2>{inline(A['values-heading'])}</h2>
  <div class="svc-grid">{rows(A['values'])}</div>
</div></section>"""

    founder = f"""<section class="section paper"><div class="wrap">
  <h2>{inline(A['founder-heading'])}</h2>
  <div class="founder gap-top-lg">
    <img src="assets/headshot-240.jpg" width="120" height="120"
      loading="lazy" decoding="async" alt="{esc(A['portrait-alt'])}">
    <div class="prose">{md(A['background-body'])}</div>
  </div>
  <div class="rule-sect"><h2 class="subhead serif">{inline(A['story-heading'])}</h2>
    <div class="prose"><p>{inline(A['story-body'])}</p></div>
    <a class="more" href="our-story.html">{inline(A['story-action'])} &rarr;</a></div>
</div></section>"""

    return page(A, "About", hero + purpose + values + founder)

# 2026-09-18 (Joseph): build_why() removed -- the "Our approach" page is
# cut. Its Mission/values went to about.md; its hero, teachers-*,
# students-* and work-* copy is still in copy/why_alcuin.md, unrendered
# and unreferenced, awaiting a decision on where (if anywhere) it lands.

# ---------------------------------------------------------------- story

def build_story():
    S = {"browser-title": "How Alcuin began | The Alcuin Project",
         "meta-description": "Joseph Dockstader on learning to use AI, the questions it raised in his teaching, and the school coaching practice that became Alcuin."}
    raw = STORY_FILE.read_text()
    raw = re.sub(r"<!--.*?-->", "", raw, flags=re.S)
    raw = re.sub(r"^# .*$", "", raw, count=1, flags=re.M)
    hero = """<section class="page-hero on-dark"><div class="wrap">
  <h1>How Alcuin began</h1>
  <p class="byline">Joseph Dockstader</p>
</div></section>"""
    essay = f"""<section class="section paper"><div class="wrap">
  <div class="prose-narrow">{md(raw)}</div>
  <div class="rule-sect narrow">
    <h2 class="subhead serif">Bring the work to your school</h2>
    <div><a class="btn" href="training.html">Explore training</a></div></div>
</div></section>"""
    # Nav highlights nothing here — same 2026-09-10 ruling as build_why.
    return page(S, "", hero + essay, ending="none")

# ---------------------------------------------------------------- privacy

def build_privacy():
    P = load_slots("privacy.md")
    email = G["footer-contact"]
    hero = f"""<section class="page-hero on-dark"><div class="wrap">
  <h1>{inline(P['hero-h1'])}</h1>
</div></section>"""
    prose = md(P["body"]).replace(
        esc(email), f'<a class="mail-link" href="mailto:{email}">{email}</a>')
    body = f"""<section class="section paper"><div class="wrap">
  <div class="prose">{prose}</div>
</div></section>"""
    return page(P, "", hero + body, ending="none")

# 2026-09-18 (Joseph): a copyright page, linked in the footer beside
# Privacy. The one-line notice in the footer base stays; this is the
# full statement it points at.
def build_copyright():
    C = load_slots("copyright.md")
    email = G["footer-contact"]
    hero = f"""<section class="page-hero on-dark"><div class="wrap">
  <h1>{inline(C['hero-h1'])}</h1>
</div></section>"""
    prose = md(C["body"]).replace(
        esc(email), f'<a class="mail-link" href="mailto:{email}">{email}</a>')
    body = f"""<section class="section paper"><div class="wrap">
  <div class="prose">{prose}</div>
  <div class="rule-sect narrow">
    <p class="soft">Permissions and licensing:
      <a class="mail-link" href="mailto:{email}">{email}</a></p></div>
</div></section>"""
    return page(C, "", hero + body, ending="none")

def build_notfound():
    N = load_slots("notfound.md")
    hero = f"""<section class="page-hero on-dark"><div class="wrap">
  <h1>{inline(N['hero-h1'])}</h1>
  <p class="lede">{inline(N['body'])}</p>
</div></section>"""
    links = "".join(
        f'<div class="col"><h3><a href="{href}">{esc(label)}</a></h3></div>'
        for label, href in NAV_ITEMS + [("Book a call", "contact.html")])
    body = f"""<section class="section paper"><div class="wrap">
  <div class="cols">{links}</div>
</div></section>"""
    # noindex regardless of PRELAUNCH: a 404 should never be in an index.
    N["force-noindex"] = "1"
    return page(N, "", hero + body, ending="none")

# ---------------------------------------------------------------- contact

def build_contact():
    C = load_slots("contact.md")
    email = G["footer-contact"]
    endpoint = C.get("config-intake-endpoint", "").strip()
    schedule = C.get("config-schedule-url", "").strip()
    hero = f"""<section class="page-hero on-dark"><div class="wrap">
  <h1>{inline(C['hero-h1'])}</h1>
  <p class="lede">{inline(C['hero-body'])}</p>
</div></section>"""

    def field(fid, label, required, ftype="text", helper="", multiline=False,
              autocomplete=""):
        req = ' required' if required else ''
        ac = f' autocomplete="{autocomplete}"' if autocomplete else ''
        tag = (f'<textarea id="{fid}" name="{fid}" rows="4"></textarea>'
               if multiline else
               f'<input id="{fid}" name="{fid}" type="{ftype}"{req}{ac}>')
        helper_html = f'<p class="helper">{esc(helper)}</p>' if helper else ''
        opt = '' if required else ' <span class="opt">(optional)</span>'
        return f"""<div class="field"><label for="{fid}">{esc(label)}{opt}</label>
  {tag}{helper_html}</div>"""

    form = rf"""<section class="section paper"><div class="wrap">
  <h2>{inline(C['details-heading'])}</h2>
  <div class="prose"><p>{inline(C['details-body'])}</p>
    <p class="soft">{inline(C['details-support'])}</p></div>

  <div class="intake" id="intake">
    <h2 class="subhead serif">{inline(C['intake-heading'])}</h2>
    <p class="soft gap-below">{inline(C['intake-intro'])}</p>
    <form id="intake-form" novalidate>
      <div class="field-row">
        {field('first', 'First name', True, autocomplete='given-name')}
        {field('last', 'Last name', True, autocomplete='family-name')}
      </div>
      {field('school', 'School or district name', True)}
      {field('position', 'Position', True, autocomplete='organization-title')}
      {field('email', 'Email address', True, ftype='email', autocomplete='email')}
      {field('phone', 'Phone number', False, ftype='tel', autocomplete='tel')}
      {field('notes', "What would you like us to discuss?", False,
             helper=C['notes-helper'], multiline=True)}
      <p class="helper">{inline(C['privacy-note'])}</p>
      <p class="form-msg" id="form-msg" role="alert" hidden></p>
      <button class="btn" id="intake-submit" type="submit">{inline(C['intake-submit'])}</button>
    </form>
  </div>

  <div class="intake" id="schedule" role="status" tabindex="-1" hidden>
    <h2 class="subhead serif">{inline(C['schedule-heading'])}</h2>
    <p class="soft gap-below">{inline(C['schedule-body'])}</p>
    <a class="btn" id="schedule-link" href="{schedule or '#'}" target="_blank" rel="noopener">{inline(C['schedule-action'])}</a>
  </div>

  <div class="rule-sect narrow">
    <p class="soft">{inline(C['email-support']).replace(esc(email), f'<a class="mail-link" href="mailto:{email}">{email}</a>')}</p>
  </div>
</div></section>
<script>
(function () {{
  var ENDPOINT = {endpoint!r};
  var SCHEDULE = {schedule!r};
  var form = document.getElementById('intake-form');
  var msg = document.getElementById('form-msg');
  var btn = document.getElementById('intake-submit');
  var intake = document.getElementById('intake');
  var scheduleBox = document.getElementById('schedule');
  if (!form) return;
  var subId = null;
  try {{
    if (sessionStorage.getItem('alcuinIntakeSaved')) {{
      intake.hidden = true; scheduleBox.hidden = false;
    }}
  }} catch (e) {{}}
  function show(text) {{ msg.textContent = text; msg.hidden = false; }}
  // Save failure must never strand the visitor: offer the calendar
  // directly and gather the details on the call instead.
  function fail() {{
    msg.textContent = {C['msg-save-failure']!r} + ' Or ';
    var a = document.createElement('a');
    a.href = SCHEDULE; a.target = '_blank'; a.rel = 'noopener';
    a.textContent = 'book your time directly';
    msg.appendChild(a);
    msg.appendChild(document.createTextNode(
      " and we'll gather these details on the call."));
    msg.hidden = false;
  }}
  form.addEventListener('submit', function (ev) {{
    ev.preventDefault();
    msg.hidden = true;
    var get = function (id) {{ return document.getElementById(id).value.trim(); }};
    var data = {{ first: get('first'), last: get('last'), school: get('school'),
      position: get('position'), email: get('email'), phone: get('phone'),
      notes: get('notes') }};
    var firstBad = null, emailBad = false;
    ['first', 'last', 'school', 'position', 'email'].forEach(function (id) {{
      var el = document.getElementById(id);
      var bad = !el.value.trim();
      if (id === 'email' && !bad &&
          !/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(el.value.trim())) {{
        bad = true; emailBad = true;
      }}
      el.setAttribute('aria-invalid', bad ? 'true' : 'false');
      el.closest('.field').classList.toggle('error', bad);
      if (bad && !firstBad) firstBad = el;
    }});
    if (firstBad) {{
      show(emailBad && firstBad.id === 'email'
           ? {C['msg-email']!r} : {C['msg-validation']!r});
      firstBad.focus();
      return;
    }}
    if (!ENDPOINT) {{ fail(); return; }}
    if (!subId) {{
      subId = (window.crypto && crypto.randomUUID) ? crypto.randomUUID()
              : String(Date.now()) + '-' + Math.random().toString(16).slice(2);
    }}
    data.id = subId;
    var btnLabel = btn.textContent;
    btn.disabled = true;
    btn.textContent = {C.get('msg-sending', 'Sending…')!r};
    fetch(ENDPOINT, {{ method: 'POST',
        headers: {{ 'Content-Type': 'text/plain;charset=utf-8' }},
        body: JSON.stringify(data) }})
      .then(function (r) {{ return r.json(); }})
      .then(function (res) {{
        if (res && res.ok) {{
          try {{ sessionStorage.setItem('alcuinIntakeSaved', '1'); }} catch (e) {{}}
          intake.hidden = true; scheduleBox.hidden = false;
          var reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
          scheduleBox.scrollIntoView({{ behavior: reduce ? 'auto' : 'smooth', block: 'center' }});
          scheduleBox.focus({{ preventScroll: true }});
        }} else {{ fail(); }}
      }})
      .catch(function () {{ fail(); }})
      .finally(function () {{ btn.disabled = false; btn.textContent = btnLabel; }});
  }});
}})();
</script>"""
    # 2026-09-18 (Joseph): "Support for school decisions" moved here from
    # training.html (copy moved to copy/contact.md). It sits above the
    # inquiry form: what school leaders come to Alcuin for, read at the
    # moment they are deciding to call.
    advisory = f"""<section class="section cream"><div class="wrap">
  <h2>{inline(C['advisory-heading'])}</h2>
  <div class="svc-grid">{rows(C['advisory'])}</div>
</div></section>"""

    body = hero + advisory + form
    # "Contact" lights no nav item; nav() puts aria-current on the CTA.
    return page(C, "Contact", body, ending="none")

# ---------------------------------------------------------------- build

def cream_mark():
    """The Alcuin mark in cream on transparent, cached across builds."""
    cache = HERE / ".build" / "mark-cream.png"
    if cache.exists():
        return cache
    cache.parent.mkdir(parents=True, exist_ok=True)
    svg = cache.parent / "mark-cream.svg"
    svg.write_text(MARK_SVG)
    try:
        subprocess.run(
            [CHROME, "--headless", "--disable-gpu",
             "--default-background-color=00000000",
             f"--screenshot={cache}", "--window-size=400,400",
             svg.as_uri()], check=True, capture_output=True, timeout=60)
    except (subprocess.SubprocessError, OSError):
        print("  ! could not render the mark; cards will omit it")
        return None
    return cache if cache.exists() else None


def wrap_to_width(draw, text, font, max_w):
    words, lines, line = text.split(), [], ""
    for w in words:
        trial = f"{line} {w}".strip()
        if draw.textlength(trial, font=font) <= max_w or not line:
            line = trial
        else:
            lines.append(line)
            line = w
    if line:
        lines.append(line)
    return lines


def build_post_card(title, date_label, dest):
    """One lead card. Title sets its own size so long titles still fit."""
    from PIL import Image, ImageDraw, ImageFont
    img = Image.new("RGB", (CARD_W, CARD_H), TEAL_RGB)
    d = ImageDraw.Draw(img)
    d.rectangle([0, 0, 12, CARD_H], fill=EMBER_RGB)

    pad, right = 78, 150
    max_w = CARD_W - pad - right
    d.text((pad, 74), date_label.upper(),
           font=ImageFont.truetype(CARD_SANS, 23), fill=SEAFOAM_RGB)

    for size in (66, 58, 50, 44):
        font = ImageFont.truetype(CARD_SERIF, size)
        lines = wrap_to_width(d, title, font, max_w)
        if len(lines) <= 4:
            break
    lead = int(size * 1.24)
    y = 168
    for line in lines[:4]:
        d.text((pad, y), line, font=font, fill=CREAM_RGB)
        y += lead

    base = CARD_H - 128
    d.line([(pad, base), (CARD_W - pad, base)], fill=(60, 88, 98), width=2)
    d.text((pad, base + 30), "The Alcuin Project",
           font=ImageFont.truetype(WATERMARK_FONT, 28), fill=CREAM_RGB)
    mark = cream_mark()
    if mark:
        m = Image.open(mark).convert("RGBA").resize((92, 92), Image.LANCZOS)
        img.paste(m, (CARD_W - pad - 92, base + 4), m)
    img.save(dest, quality=88, optimize=True, progressive=True)
    return dest


def build_classroom():
    """Web-sized copies of the room photograph. Never upscales."""
    if not CLASSROOM.exists():
        return []
    from PIL import Image
    src = Image.open(CLASSROOM).convert("RGB")
    made = []
    for w in CLASSROOM_WIDTHS:
        if w > src.width:
            continue
        h = round(src.height * w / src.width)
        img = src if w == src.width else src.resize((w, h), Image.LANCZOS)
        dest = OUT / "assets" / f"classroom-{w}.jpg"
        img.save(dest, quality=84, optimize=True, progressive=True)
        made.append((w, h, dest.name))
    # drop sizes left behind by an earlier CLASSROOM_WIDTHS, so the
    # assets folder never carries widths nothing references
    keep = {d.name for _w, _h, d in
            [(w, h, OUT / "assets" / n) for w, h, n in made]}
    for old in (OUT / "assets").glob("classroom-*.jpg"):
        if old.name not in keep:
            old.unlink()
    return made


# Guides (2026-09-18): reference pages that answer one question a
# school leader actually types, at a clean exact-match URL. Unlike posts
# they carry no date and do not age -- they are the pages meant to rank.
# One file per guide in copy/guides/; the filename is the URL.
def load_guides():
    folder = COPY / "guides"
    if not folder.is_dir():
        return []
    out = []
    for f in sorted(folder.glob("*.md")):
        if f.name == "README.md":
            continue
        g = load_slots(f"guides/{f.name}")
        if not g.get("body"):
            print(f"  ! skipping guides/{f.name}: no body")
            continue
        out.append((f.stem, g))
    # Explicit running order: an "order" slot, low number first. Guides
    # without one fall to the end, alphabetically. Filename order put
    # Arizona first, which is not where a first-time reader should land.
    out.sort(key=lambda kv: (int(kv[1].get("order", 999)), kv[0]))
    return out



def related_guides(slug, guides, want=3):
    """Pick sibling guides to link from the foot of one guide.

    THE GUARANTEE THAT MATTERS: before this existed, 8 of 13 guides had
    zero inbound links from any sibling -- only the hub linked to them,
    so the library was a wheel with no spokes. Topic-similarity alone
    does not fix that; a lopsided group leaves some guide unlinked.

    So the picker is same-group siblings PLUS the next guide in global
    order, wrapping. The wrap makes a cycle through every guide, which
    means each one receives at least one inbound link no matter how the
    groups are shaped. Relevance on top of a guaranteed floor.
    """
    order = [s for s, _g in guides]
    if slug not in order:
        return []
    i = order.index(slug)
    by_slug = dict(guides)
    mine = (by_slug[slug].get("group") or "").strip()

    picked = []
    # same group first, in publication order, excluding self
    for s, g in guides:
        if s != slug and (g.get("group") or "").strip() == mine:
            picked.append(s)
    picked = picked[:max(0, want - 1)]

    # then the successor in global order, which is what closes the cycle
    nxt = order[(i + 1) % len(order)]
    if nxt != slug and nxt not in picked:
        picked.append(nxt)

    # top up from the rotation if still short
    k = 2
    while len(picked) < want and k <= len(order):
        cand = order[(i + k) % len(order)]
        if cand != slug and cand not in picked:
            picked.append(cand)
        k += 1
    return [(s, by_slug[s]) for s in picked[:want]]


def related_band(slug, guides):
    items = related_guides(slug, guides)
    if not items:
        return ""
    cards = "".join(f"""<a class="rel-card" href="{s}.html">
  <span class="rel-tag">{esc(g.get('group') or 'Guide')}</span>
  <span class="rel-h">{inline(g['hero-h1'])}</span>
  <span class="rel-p">{inline(g['hero-body'])}</span>
</a>""" for s, g in items)
    return f"""<section class="section tight paper"><div class="wrap">
  <h2 class="h2-sm">Related guides</h2>
  <div class="rel-grid">{cards}</div>
</div></section>"""


def guide_jsonld(slug, G):
    """Article + BreadcrumbList for a guide page."""
    import json as _json
    url = f"{SITE_URL}/{slug}.html"
    art = {
        "@context": "https://schema.org",
        "@type": "Article",
        "headline": strip_tags(inline(G["hero-h1"]))[:110],
        "description": strip_tags(inline(G.get("hero-body", ""))),
        "mainEntityOfPage": {"@type": "WebPage", "@id": url},
        "url": url,
        "inLanguage": "en-US",
        "isAccessibleForFree": True,
        "author": {"@type": "Organization", "name": "The Alcuin Project",
                   "url": SITE_URL + "/"},
        "publisher": {"@type": "Organization", "name": "The Alcuin Project",
                      "url": SITE_URL + "/"},
    }
    crumbs = {
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Home",
             "item": SITE_URL + "/"},
            {"@type": "ListItem", "position": 2, "name": "Guides",
             "item": SITE_URL + "/guides.html"},
            {"@type": "ListItem", "position": 3,
             "name": strip_tags(inline(G["hero-h1"])), "item": url},
        ],
    }
    dump = lambda d: ('<script type="application/ld+json">'
                      + _json.dumps(d, ensure_ascii=False) + "</script>")
    return dump(art) + dump(crumbs)


def strip_tags(t):
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", "", t or "")).strip()


def build_guide(slug, G, guides=()):
    hero = f"""<section class="page-hero on-dark"><div class="wrap">
  <div class="kicker">{inline(G['hero-eyebrow'])}</div>
  <h1>{inline(G['hero-h1'])}</h1>
  <p class="lede">{inline(G['hero-body'])}</p>
</div></section>"""
    body = f"""<section class="section paper"><div class="wrap">
  <div class="guide-prose">{md(G['body'])}</div>
</div></section>
<section class="section tight cta-dark on-dark"><div class="wrap">
  <h2 class="h2-sm">{inline(G['cta-heading'])}</h2>
  <p class="narrow gap-top">{inline(G['cta-body'])}</p>
  <div class="gap-top-lg"><a class="btn" href="contact.html">{inline(G['cta-action'])}</a></div>
</div></section>"""
    body += """<section class="section tight paper"><div class="wrap">
  <a class="more" href="guides.html">&larr; All guides</a>
</div></section>"""
    G["share-title"] = G["hero-h1"]
    G["extra-jsonld"] = guide_jsonld(slug, G)
    rel = related_band(slug, guides)
    # Related band sits between the prose and the "All guides" link, so
    # the reader meets siblings before the exit.
    body = body.replace('<section class="section tight paper"><div class="wrap">\n  <a class="more"', rel + '<section class="section tight paper"><div class="wrap">\n  <a class="more"', 1)
    return page(G, "Guides", hero + body, ending="none")


def load_alerts(limit=14):
    """Recent developments for the board, from copy/alerts.md.

    Reverse chronological, newest first. Two hard rules, both enforced
    here rather than trusted to whoever edits the file:

      * an item must carry a `url`, because the whole point is that a
        reader can go read the thing themselves; and
      * an item marked `draft: yes` never renders, so an unverified
        link can sit in the file without reaching the site.

    `limit` caps what shows. Older items stay in the file as the
    running record.
    """
    f = COPY / "alerts.md"
    if not f.is_file():
        return []
    raw = "\n".join(l for l in f.read_text().splitlines()
                    if not l.startswith("#"))
    out = []
    for block in raw.split("\n---\n"):
        d = {}
        for line in block.strip().splitlines():
            if ":" in line:
                k, _, v = line.partition(":")
                d[k.strip()] = v.strip()
        if not d.get("date"):
            continue
        if d.get("draft", "").lower() in ("yes", "true"):
            print(f"  - development held as draft: {d.get('headline','?')[:48]}")
            continue
        # A link is preferred, not required (Joseph, 2026-09-18): a
        # figure we can attribute in words does not need a hyperlink.
        # `source` still carries the attribution either way.
        try:
            d["_date"] = dt.date.fromisoformat(d["date"])
        except ValueError:
            print(f"  ! alerts.md: bad date {d['date']!r}, skipped")
            continue
        out.append(d)
    out.sort(key=lambda x: x["_date"], reverse=True)
    return out[:limit]


def board_band(items):
    """The developments board. Renders nothing when nothing qualifies."""
    if not items:
        return ""
    today = dt.date.today()
    rows = []
    for a in items:
        age = (today - a["_date"]).days
        when = ("today" if age == 0 else
                "yesterday" if age == 1 else
                f"{age} days ago" if age < 45 else "")
        guide = ""
        if a.get("guide"):
            guide = (f'<span class="also">Related: '
                     f'<a href="{a["guide"]}.html">'
                     f'{esc(a.get("guide-label", "our guide"))}</a></span>')
        # With a url, the source becomes a link. Without one, it is
        # still named -- an unsourced figure has no business here.
        if a.get("url"):
            read = (f'<a class="read" href="{esc(a["url"])}" target="_blank" '
                    f'rel="noopener noreferrer">Read it at '
                    f'{esc(a.get("source", "the source"))}'
                    f'<span class="ex" aria-hidden="true">&#8599;</span>'
                    f'<span class="sr-only"> (opens in a new tab)</span></a>')
        elif a.get("source"):
            read = f'<span class="attrib">{esc(a["source"])}</span>'
        else:
            read = ""
        stat = (f'<span class="stat">{esc(a["stat"])}</span>'
                if a.get("stat") else "")
        rows.append(f"""<div class="item{' figure' if stat else ''}">
  <div class="d">{esc(a.get('display') or a['date'])}
    {f'<small>{when}</small>' if when else ''}</div>
  <div>
    {stat}
    <div class="h"><span class="w">{esc(a.get('where', ''))}</span>{esc(a['headline'])}</div>
    <div class="s">{esc(a.get('detail', ''))}</div>
    {read}
    {guide}
  </div>
</div>""")
    return f"""<section class="section paper"><div class="wrap">
  <div class="board-head"><h2 class="h2-sm">Recent Developments</h2></div>
  <p class="board-note">Rules, funding, and decisions that affect how schools
  use AI.</p>
  <div class="board">{''.join(rows)}</div>
  <p class="board-foot">Checked {today.strftime('%B %-d, %Y')}.</p>
</div></section>"""


def build_guides_index():
    G = load_slots("guides_index.md")
    guides = load_guides()
    hero = f"""<section class="page-hero on-dark"><div class="wrap">
  <h1>{inline(G['hero-h1'])}</h1>
  <p class="lede">{inline(G['hero-body'])}</p>
</div></section>"""
    band = board_band(load_alerts())

    # 2026-09-18 (Joseph): chips over a single grid, replacing the rail
    # added earlier the same day. The whole library is visible first and
    # a chip narrows it; clicking the active chip clears the filter.
    # Groups come from each guide's own "## group" slot, so re-grouping
    # is a copy edit rather than a code change.
    if guides:
        order, seen = [], set()
        for _slug, g in guides:
            grp = g.get("group") or "Other"
            if grp not in seen:
                seen.add(grp); order.append(grp)
        counts = {}
        for _slug, g in guides:
            grp = g.get("group") or "Other"
            counts[grp] = counts.get(grp, 0) + 1

        chips = (f'<button class="chip" type="button" aria-pressed="false" '
                 f'data-g="all">All<span class="n">{len(guides)}</span>'
                 f'</button>')
        chips += "".join(
            f'<button class="chip" type="button" aria-pressed="false" '
            f'data-g="{esc(grp)}">{esc(grp)}'
            f'<span class="n">{counts[grp]}</span></button>'
            for grp in order)

        cards = "".join(f"""<article class="g-card" data-g="{esc(g.get('group') or 'Other')}">
  <p class="g-tag">{esc(g.get('group') or 'Other')}</p>
  <h2><a href="{slug}.html">{inline(g['hero-h1'])}</a></h2>
  <p>{inline(g['hero-body'])}</p>
  <a class="more" href="{slug}.html">Read the guide &rarr;</a>
</article>""" for slug, g in guides)

        listing = f"""<section class="section cream"><div class="wrap">
  <div class="chips" role="group" aria-label="Filter guides by topic">
    {chips}
  </div>
  <div class="g-grid">{cards}</div>
  <p class="chip-empty" id="chip-empty" hidden>No guide in that topic yet.</p>
</div></section>"""
    else:
        listing = f"""<section class="section cream"><div class="wrap">
  <p class="intro">{inline(G['empty-note'])}</p>
</div></section>"""
    return page(G, "Guides", hero + listing + band)

def build_post_cards(posts):
    made = []
    for slug, P in posts:
        dest = OUT / "assets" / f"card-{slug}.jpg"
        build_post_card(P["title"], pretty_date(P["date"]), dest)
        made.append(dest.name)
    return made


def build_poster_previews():
    """Derive watermarked, downscaled poster previews from the masters.

    Nothing here is printable: a 1100px-tall JPEG is about 30 DPI at
    24x36, and the watermark is burned into the pixels rather than
    overlaid in CSS, so saving the image still gets you a watermark.
    This is deterrence, not protection -- see the note in build_products.
    """
    from PIL import Image, ImageDraw, ImageFont
    made = []
    for slug, fname in POSTERS:
        src = POSTER_SRC / fname
        if not src.exists():
            print(f"  ! missing poster master: {src}")
            continue
        master = Image.open(src).convert("RGB")
        for kind, height, mark in (("thumb", POSTER_THUMB_H, False),
                                   ("preview", POSTER_PREVIEW_H, True)):
            w = round(master.width * height / master.height)
            img = master.resize((w, height), Image.LANCZOS)
            if mark:
                img = watermark(img)
            out = OUT / "assets" / f"poster-{slug}-{kind}.jpg"
            img.save(out, quality=88, optimize=True, progressive=True)
            made.append(out.name)
    return made


def watermark(img):
    """Burn a repeating diagonal wordmark across the preview."""
    from PIL import Image, ImageDraw, ImageFont
    layer = Image.new("RGBA", img.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(layer)
    size = max(18, img.width // 22)
    try:
        font = ImageFont.truetype(WATERMARK_FONT, size)
    except OSError:
        font = ImageFont.load_default()
    text = "THE ALCUIN PROJECT  ·  PREVIEW  ·  NOT FOR PRINT"
    tw = draw.textlength(text, font=font)
    step_y = int(size * 5.5)
    for row, y in enumerate(range(-img.height, img.height * 2, step_y)):
        offset = int(row * tw / 3) % int(tw + size * 4)
        for x in range(-int(tw) - offset, img.width + int(tw),
                       int(tw + size * 4)):
            draw.text((x + offset, y), text, font=font,
                      fill=(255, 255, 255, 62))
            draw.text((x + offset + 1, y + 1), text, font=font,
                      fill=(0, 0, 0, 40))
    layer = layer.rotate(30, resample=Image.BICUBIC, center=(
        img.width // 2, img.height // 2))
    return Image.alpha_composite(img.convert("RGBA"), layer).convert("RGB")


def write_robots_and_sitemap(names):
    """robots.txt and sitemap.xml -- what a crawler looks for first.

    Under PRELAUNCH the robots file disallows everything, so a staging
    copy cannot be indexed by accident.
    """
    if PRELAUNCH:
        (OUT / "robots.txt").write_text(
            "User-agent: *\nDisallow: /\n")
        (OUT / "sitemap.xml").unlink(missing_ok=True)
        return
    (OUT / "robots.txt").write_text(
        "User-agent: *\nAllow: /\n\n"
        f"Sitemap: {SITE_URL}/sitemap.xml\n")
    today = datetime.date.today().isoformat()
    urls = ""
    for n in names:
        loc = SITE_URL + "/" + ("" if n == "index.html" else n)
        urls += (f"  <url><loc>{loc}</loc>"
                 f"<lastmod>{today}</lastmod></url>\n")
    (OUT / "sitemap.xml").write_text(
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        f"{urls}</urlset>\n")


def main():
    OUT.mkdir(exist_ok=True)
    (OUT / "assets").mkdir(exist_ok=True)
    # Headshot ships as sized JPEGs, regenerated from the original on
    # every build (the 1254px source in content-drop/ is never touched).
    # 240px serves the 120px homepage circle at 2x; 360px serves the
    # 180px About portrait at 2x.
    if HEADSHOT.exists():
        for size in (240, 360):
            dest = OUT / "assets" / f"headshot-{size}.jpg"
            try:
                subprocess.run(
                    ["sips", "-s", "format", "jpeg", "-s", "formatOptions", "80",
                     "-Z", str(size), str(HEADSHOT), "--out", str(dest)],
                    check=True, capture_output=True)
            except (OSError, subprocess.CalledProcessError):
                # sips is macOS-only; Pillow does the same resize elsewhere.
                im = Image.open(HEADSHOT).convert("RGB")
                im.thumbnail((size, size), Image.LANCZOS)
                im.save(dest, "JPEG", quality=80)
    rooms = build_classroom()
    if rooms:
        print(f"  classroom: {', '.join(str(w) for w, _h, _n in rooms)}")
    shots = build_poster_previews()
    if shots:
        print(f"  poster previews: {len(shots)}")
    # assets-src files are copied in verbatim. Prune PDFs that no longer
    # have a source: renaming the curriculum volume to the standards
    # volume left the old alcuin-curriculum.pdf sitting in the output,
    # downloadable by anyone with the URL. Only PDFs are pruned here --
    # every other asset in the folder is generated by this script.
    src_names = {f.name for f in (HERE / "assets-src").glob("*")
                 if f.is_file() and not f.name.startswith(".")}
    for f in (HERE / "assets-src").glob("*"):
        if f.is_file() and not f.name.startswith("."):
            shutil.copy(f, OUT / "assets" / f.name)
    for stale in (OUT / "assets").glob("*.pdf"):
        if stale.name not in src_names:
            stale.unlink()
            print(f"  pruned stale asset: {stale.name}")
    # The Gmail signature (email_signature.html) and every email already
    # sent load the mark from /mark.png at the site root. It lived in the
    # old live/ placeholder deploy and 404'd once redesign/ replaced it.
    if (HERE / "live" / "mark.png").exists():
        shutil.copy(HERE / "live" / "mark.png", OUT / "mark.png")
    else:
        print("  ! missing live/mark.png; site icon not copied")
    pages = {
        "index.html": build_home(),
        "training.html": build_training(),
        "frameworks.html": build_frameworks(),
        "curriculum.html": build_curriculum(),
        "guides.html": build_guides_index(),
        "blog.html": build_blog(),
        "about.html": build_about(),
        "our-story.html": build_story(),
        "privacy.html": build_privacy(),
        "copyright.html": build_copyright(),
        "contact.html": build_contact(),
        "404.html": build_notfound(),
    }
    blog_slots = load_slots("blog.md")
    cards = build_post_cards(load_posts())
    if cards:
        print(f"  post cards: {len(cards)}")
    for slug, post in load_posts():
        pages[post_page_name(slug)] = build_post(slug, post, blog_slots)
    _all_guides = load_guides()
    for slug, guide in _all_guides:
        pages[f"{slug}.html"] = build_guide(slug, guide, _all_guides)
    for name, html in pages.items():
        canon = SITE_URL + "/" + ("" if name == "index.html" else name)
        html = html.replace(CANON_TOKEN, canon)
        (OUT / name).write_text(html)
        print(f"  built {name}")
    write_robots_and_sitemap(
        sorted(n for n in pages if n != "404.html"))
    print(f"\n{len(pages)} pages -> {OUT} (story: {STORY_FILE.name})")


if __name__ == "__main__":
    main()

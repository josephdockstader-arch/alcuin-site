# Alcuin Project website

Source for [alcuinproject.com](https://alcuinproject.com), the site for my AI literacy and teacher-training consultancy. I built it with Claude Code. I wrote the specifications and the copy, made the design decisions, and directed and reviewed the code. [HISTORY.md](HISTORY.md) records how it was built, round by round.

## The problem it solves

I'm the only person who maintains this site, and I'm not a web developer. I needed a site I could change one sentence at a time without editing HTML, without a monthly page-builder fee, and without breaking something every time I published.

## How it works

```
copy/*.md  ──►  build_redesign.py  ──►  redesign/  ──►  Cloudflare Pages
   ▲                                       │
   └────────  edit_server.py + editor/  ◄──┘
             (click a line, change it, it's written back to copy/)
```

- **Content lives in plain Markdown.** Every page's text sits in `copy/*.md`, one `## slot` per piece of the page. Guides are in `copy/guides/`, blog posts in `copy/posts/`, and the state-law tracker in `copy/alerts.md`. Lines starting with `#` are editorial notes, often recording where a fact was verified. The build strips them, so they never reach a page.
- **One script builds the site.** `build_redesign.py` reads the copy files and writes static HTML, CSS, and JavaScript to `redesign/`, along with the sitemap and structured data.
- **A local editor for changing text in place.** `edit_server.py` serves the built site with an **Edit text** button (`editor/`). Clicking any line on the page edits it, and the change is written back to the matching line in the Markdown source. The site then rebuilds and reloads, and a message says which file and line changed.
- **Publishing with a check before anything goes live.** The editor's **Publish** button rebuilds the site, lists every file that differs from the last deploy, and deploys to Cloudflare Pages only after I approve the list.

## Running it

Requires Python 3.9 or later and Pillow (`pip install -r requirements.txt`). Deploying also needs Node.js (for `npx wrangler`) and access to the Cloudflare account.

```bash
python3 build_redesign.py      # build the site into redesign/
python3 edit_server.py         # open the editor at http://localhost:8788
```

`EDITOR.md` covers day-to-day use of the editor.

## Cases the system handles

- **Text the editor can't place.** If clicked text is hard-coded in the build script or assembled from several slots, the editor says so and names where to edit it, instead of guessing.
- **The same words in two places.** If a line appears in more than one slot, the editor lists the matches and asks which one to change.
- **A lost edit.** All copy is backed up to `.backups/` each time the editor starts.
- **A deploy made some other way.** `python3 edit_server.py --snapshot` resets the comparison point so the publish check stays accurate.
- **Port already in use.** The editor says so and points to `ALCUIN_PORT` to pick another one.
- **Missing images.** The build skips any image source it can't find and prints a warning. The poster artwork is a paid product, so it isn't in this repo, and the poster previews are skipped here.
- **Draft items.** A tracker row marked `draft: yes` stays in the file and never renders, so research can be parked until it is confirmed.

## Checks

- `python3 tools/contrast_check.py` tests every color pair in the design against WCAG contrast thresholds (4.5:1 for text, 3:1 for controls). Run it after any color change.
- Each round of changes in HISTORY.md ends with what was verified and how.

## Handing it over

Everything someone else would need to keep it running:

| Piece | Where it lives |
|---|---|
| Hosting | Cloudflare Pages, project `alcuinproject`, deployed with `npx wrangler pages deploy redesign --project-name=alcuinproject` |
| Domain and DNS | Cloudflare Registrar, same Cloudflare account |
| Search indexing | Google Search Console, verified through Cloudflare DNS |
| Booking form | A Google Apps Script web app writing to a private Google Sheet; the endpoint URL is in `copy/contact.md` under `config-intake-endpoint` |
| Newsletter signups | A second Apps Script and Sheet, kept separate from booking contacts; the endpoint URL is in `copy/global.md` under `config-signup-endpoint` |
| Booking calendar | Google Calendar appointment page on the business Google Workspace account |

The Apps Script source is kept outside this repo.

## What's not in this repo

The poster artwork, superseded drafts, planning documents, and the deploy snapshots. The images and PDFs included here are the same files the live site already serves.

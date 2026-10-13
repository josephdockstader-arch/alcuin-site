# Alcuin Project website

Source for [alcuinproject.com](https://alcuinproject.com), the site for my AI literacy and teacher-training consultancy. I built it with Claude Code. I wrote the specifications and the copy, and directed and reviewed the code.

## How it works

- **Content lives in plain Markdown.** Every page's text sits in `copy/*.md`, one `## slot` per piece of the page. Guides are in `copy/guides/`, blog posts in `copy/posts/`, and state-law alerts in `copy/alerts.md`. Lines starting with `#` are editorial notes and never reach the page.
- **One script builds the site.** `build_redesign.py` reads the copy files and writes static HTML, CSS, and JavaScript to `redesign/`, along with the sitemap and structured data.
- **A local editor for changing text in place.** `edit_server.py` serves the built site at `localhost:8788` with an **Edit text** button (`editor/`). Clicking any line on the page edits it, and the change is written back to the matching line in the Markdown source. The site then rebuilds and reloads. The copy is backed up each time the server starts.
- **Publishing with a check before it goes live.** The editor's **Publish** button rebuilds the site, lists every file that differs from the last deploy, and deploys to Cloudflare Pages only after I approve the list.

See `EDITOR.md` for the editor's day-to-day instructions.

## What's not in this repo

Images, the downloadable framework PDFs, and the poster source files live outside this folder, so the repo shows the code and content without reproducing the full build.

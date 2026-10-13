# Build history

This repo was published in October 2026, after the site was already live, so the git history starts there. This file records how the site was built, taken from the project's working log. Each round lists what changed and how it was checked.

## August 25 — Plan and requirements

I set the requirements before any code: one domain, minimal monthly cost, no drag-and-drop builder (all edits through Claude Code), no phone number on the site, and pricing by proposal only. The launch bar was that someone could search for the business and find it.

I chose static hosting on Cloudflare Pages (free tier) over a hosted page builder, with page text kept in Markdown so a one-word change would be a one-line edit.

I had Claude build four working homepage directions so I could compare them side by side instead of describing them in the abstract. I chose the consultancy layout and asked for the brand's animated logo to be moved into its header.

## August 27 — First full mock-up

All ten pages built from `copy/*.md` by a single script. The Our Story page went through five drafts that day.

## September 8 — Redesign and outside review

I brought a designer's mock-up and had it built across the site as a separate build, so the working version stayed untouched until the new one was approved. That build became `build_redesign.py`.

I then put the site through an adversarial review, which returned 15 findings. I accepted most, rejected some (I restored the company's original core values after the review softened them), and supplied replacement copy for every page. Two rules came out of this round and are still enforced by the build:

- Editorial notes in the copy files are stripped from every rendered page, so internal comments can never leak onto the site.
- No page explains why something is absent. If a product isn't offered, the page doesn't mention it.

Checked: no stray single words on their own line at 320px, a one-row mobile header, a working menu toggle, no horizontal scrolling at 320, 390, or 1280px, and no internal notes in the output.

## September 9 — Booking flow

A two-step booking flow: a short intake form, then a hand-off to a Google Calendar booking page. The form validates each field, stays safe if someone submits twice, and writes to a private Google Sheet through a Google Apps Script endpoint.

Checked on the live site: a submission writes one row, a repeated submission is ignored, a spreadsheet formula typed into a field is stored as plain text, and the form moves to the calendar step.

## September 10 — Design audit, three passes

I ran the site against Dieter Rams' ten principles of good design as a scored audit (30 points). It scored 13, then 19, then 22 over three passes that day. The work between passes:

- Every color, spacing value, and font size moved into named design tokens.
- The site's orange failed accessibility contrast as text, so a darker orange was added for text and buttons. `tools/contrast_check.py` now tests all 19 color pairs, and all pass.
- Keyboard focus states, form error messages tied to their fields, a skip link, and reduced-motion support added on every page.
- Images resized at build time, which cut the homepage's weight from 2.0 MB to 44 KB.
- Newsletter signups wired to their own sheet, kept separate from booking contacts.

## September 18 — Launch

The site went live on alcuinproject.com, and Search Console verified ownership through Cloudflare DNS. Shipped the same day:

- A library of 13 guides for school leaders, filterable by topic.
- A "Related guides" band at the foot of every guide. Eight of the 13 guides had no links from any other guide. Linking each guide to the next one in a loop means no guide can be left without links, whatever the topic groups look like. The count went from 8 to 0.
- A tracker of state AI laws and policies for schools. Before launch, a separate fact-check of all 14 entries found 5 wrong and 7 imprecise against their primary sources, including one state's parental-consent rule stated backwards. All were corrected. The rule for counting a state is written down: it counts only if a policy places a binding duty on school districts.

Two bugs from that day:

- The topic filter appeared to work but hid nothing. The cards' layout style overrode the browser's rule for hidden elements, so the cards were marked hidden and still showed. Fixed with one global rule. Filters are now checked by what is actually displayed on the page.
- Switching topic tabs hid the tab bar itself, because the tabs and the panels shared the same attribute. The panels got their own attribute.

## September 24 — Entry animation removed

The homepage opened on a full-screen animation that cleared when the visitor moved the mouse. Analytics showed visitors weren't getting past the home page, so I turned it off. The code stays in the build behind one setting, `SHOW_SPLASH`.

## September 25 — Local editor

`edit_server.py` and `editor/`: click any text on a page to change it, save to write it back to the Markdown source and rebuild, and publish with a list of changed files to approve before deploying.

Checked with a hero-paragraph edit and a guide paragraph containing bold text and a link. Both files were byte-identical to the originals after the change was reverted.

## September 29 — Tracker refresh, first live use of the editor

Four new tracker entries were added, and every fact was checked against its primary source. Three entries that couldn't yet be confirmed were held back as drafts. I published the update through the editor's Publish button, and the live site was checked afterward.

## October 13 — Public repo

I published this repo and made the build portable. It now runs on a fresh clone without the original project folders: images fall back to the copies in `images/`, missing files print a warning instead of stopping the build, image resizing falls back to Pillow when the macOS `sips` tool isn't available, and the editor's port and Node path can be set with environment variables.

Checked by building and running the editor from a clean copy, on a PATH with no macOS tools, and by an edit round-trip through the editor's save endpoint.

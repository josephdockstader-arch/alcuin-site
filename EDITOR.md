# Alcuin site editor (local)

The same edit-in-the-browser setup the devotional site has, for
alcuinproject.com.

## Start it
Double-click `edit.command` (this folder), or in a terminal:

    cd ".../projects/ai-pd-business/site" && python3 edit_server.py

It opens http://localhost:8788. Devotional runs on 8787, so both can run.

## Use it
1. Browse to the page. Click **Edit text** (bottom right).
2. Click any heading, paragraph, list item, button label, or footer line.
   Type the change. **Save** (or Cmd-Enter). Esc cancels.
3. The change is written to the matching line in `copy/*.md` (or the
   story file / guides / posts), the site rebuilds (about a second), and
   the page reloads with a toast saying which file and line took it.
4. **Publish** rebuilds, lists the files that differ from the last deploy,
   and on OK runs the Cloudflare deploy
   (`npx wrangler pages deploy redesign --project-name=alcuinproject`).
   Cloudflare shows the change within about a minute.

## When the editor says no
- "Couldn't map this text back to a line": the text is hard-wired in
  `build_redesign.py` (nav labels, "Related guides", form field labels,
  dates) or assembled from several slots. Edit it there.
- "This text is in N places": the same words live in two slots (for
  example "Book a call" is both `cta-label` and `inquiry-action` in
  global.md). A prompt lists them; type the number.
- A line that shares its source line with an `<!-- -->` comment is left
  alone; edit the file.
- Meta descriptions, alt text, and browser titles are not on the page,
  so they are edited in the copy files.

## Safety
- `copy/` and the story file are backed up to `.backups/copy-<timestamp>/`
  every time the server starts.
- `.published/` is a snapshot of the last deploy; Publish compares against
  it. If you ever deploy some other way, run
  `python3 edit_server.py --snapshot` afterwards so the comparison stays
  honest.

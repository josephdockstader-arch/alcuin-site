/* In-place text editor for the Alcuin site (local edit server only).
   Click "Edit text", then click any block; Save writes the change back to
   copy/*.md and rebuilds the site. Publish deploys to Cloudflare Pages. */
(function () {
  "use strict";

  // Any text-bearing element. markEditables() keeps only the leaves, so a
  // <li> that holds its own <p> is skipped in favour of the <p>.
  var SELECTORS = [
    "h1", "h2", "h3", "h4", "p", "li", "blockquote", "figcaption",
    "dt", "dd", "label", "small", "cite", "summary",
    "a.btn", "button.btn", "button[type=submit]",
    "nav .item", ".eyebrow", ".byline", ".lede", ".support",
    ".board .s", ".board .stat", ".fname", ".name"
  ];
  var SEL = SELECTORS.join(",");
  var BLOCKY = "p,li,ul,ol,h1,h2,h3,h4,div,section,blockquote,figure,form";

  var editing = false;
  var active = null;
  var origHTML = "";

  // ---------------------------------------------------------------- chrome

  var btn = el("button", "editmode-btn", "✎ Edit text");
  document.body.appendChild(btn);

  var bar = el("div", "edit-toolbar", "");
  var saveBtn = el("button", "edit-save", "Save");
  var cancelBtn = el("button", "edit-cancel", "Cancel");
  var hint = el("span", "edit-hint", "⌘↩ save · esc cancel");
  bar.appendChild(saveBtn);
  bar.appendChild(cancelBtn);
  bar.appendChild(hint);
  bar.hidden = true;
  document.body.appendChild(bar);

  var toast = el("div", "edit-toast", "");
  toast.hidden = true;
  document.body.appendChild(toast);

  var pubBtn = el("button", "publish-btn", "↑ Publish");
  document.body.appendChild(pubBtn);

  function el(tag, id, text) {
    var e = document.createElement(tag);
    e.id = id;
    if (text) e.textContent = text;
    return e;
  }

  function showToast(msg, isError, ms) {
    toast.textContent = msg;
    toast.className = isError ? "error" : "";
    toast.hidden = false;
    clearTimeout(toast._t);
    toast._t = setTimeout(function () { toast.hidden = true; },
                          ms || (isError ? 7000 : 2500));
  }

  // ------------------------------------------------------------ edit mode

  btn.addEventListener("click", function () {
    if (editing && active) {
      if (!confirmDiscard()) return;
      stopEditing(true);
    }
    editing = !editing;
    document.body.classList.toggle("editing", editing);
    btn.textContent = editing ? "✕ Done" : "✎ Edit text";
    markEditables(editing);
  });

  function isEditable(node) {
    if (node.closest("#edit-toolbar,#edit-toast,#editmode-btn,#publish-btn")) return false;
    if (node.classList.contains("skip") || node.classList.contains("sr-only")) return false;
    if (node.querySelector(BLOCKY)) return false;          // not a leaf
    if (!node.textContent.trim()) return false;
    return true;
  }

  function markEditables(on) {
    var nodes = document.querySelectorAll(SEL);
    for (var i = 0; i < nodes.length; i++) {
      if (!on) { nodes[i].classList.remove("editable-block"); continue; }
      if (isEditable(nodes[i])) nodes[i].classList.add("editable-block");
    }
  }

  function normText(h) {
    return h.replace(/<br\s*\/?>/gi, " ")
            .replace(/<\/?(div|p)[^>]*>/gi, " ")
            .replace(/&nbsp;/g, " ")
            .replace(/\s+/g, " ").trim();
  }

  function confirmDiscard() {
    if (!active) return true;
    if (normText(active.innerHTML) === normText(origHTML)) return true;
    return window.confirm("Discard the unsaved change to this block?");
  }

  document.addEventListener("click", function (e) {
    if (!editing) return;
    var target = e.target.closest(".editable-block");
    var link = e.target.closest("a,button");
    if (target) {
      if (link) { e.preventDefault(); e.stopPropagation(); }
      if (target === active) return;
      if (!confirmDiscard()) { e.preventDefault(); return; }
      stopEditing(true);
      startEditing(target);
    } else if (active && !bar.contains(e.target) && e.target !== btn) {
      if (confirmDiscard()) stopEditing(true);
    }
  }, true);

  // a nav link or button being edited must not navigate on keypress either
  document.addEventListener("submit", function (e) {
    if (editing) e.preventDefault();
  }, true);

  function startEditing(node) {
    active = node;
    origHTML = node.innerHTML;
    node.setAttribute("contenteditable", "true");
    node.classList.add("editing-now");
    node.focus();
    bar.hidden = false;
  }

  function stopEditing(revert) {
    if (!active) return;
    if (revert) active.innerHTML = origHTML;
    active.removeAttribute("contenteditable");
    active.classList.remove("editing-now");
    active = null;
    bar.hidden = true;
  }

  // ----------------------------------------------------------------- save

  function save() {
    if (!active) return;
    var newHTML = active.innerHTML;
    if (normText(newHTML) === normText(origHTML)) {
      stopEditing(true);
      return;
    }
    saveBtn.disabled = true;
    saveBtn.textContent = "Saving…";
    fetch("/api/save", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        page: pageSlug(),
        old_html: origHTML,
        new_html: newHTML
      })
    }).then(function (r) { return r.json(); }).then(function (d) {
      saveBtn.disabled = false;
      saveBtn.textContent = "Save";
      if (d.ok) {
        try {
          sessionStorage.setItem("al-scroll", String(window.scrollY));
          sessionStorage.setItem("al-editing", "1");
          sessionStorage.setItem("al-saved", d.file + " line " + d.line);
        } catch (err) { /* private mode etc. */ }
        window.location.reload();
      } else {
        showToast(d.error || "Save failed.", true);
      }
    }).catch(function () {
      saveBtn.disabled = false;
      saveBtn.textContent = "Save";
      showToast("Couldn't reach the edit server. Is it still running?", true);
    });
  }

  // -------------------------------------------------------------- publish
  // Two round trips: a dry run lists the files that differ from the last
  // deploy, then a confirm runs wrangler.

  function publishCall(body) {
    return fetch("/api/publish", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body)
    }).then(function (r) { return r.json(); });
  }

  function publishFailed(d) {
    showToast(d.error || "Publish failed.", true, 15000);
  }

  pubBtn.addEventListener("click", function () {
    if (active && !confirmDiscard()) return;
    if (active) stopEditing(true);
    pubBtn.disabled = true;
    pubBtn.textContent = "Checking…";
    publishCall({ dry: true }).then(function (d) {
      if (!d.ok) { publishFailed(d); return; }
      if (!d.changed || !d.changed.length) {
        showToast("alcuinproject.com already matches. Nothing to push.");
        return;
      }
      var list = d.changed.slice(0, 14).join("\n  ");
      if (d.changed.length > 14) list += "\n  … and " + (d.changed.length - 14) + " more";
      var go = window.confirm(
        "Publish these " + d.changed.length +
        " file(s) to alcuinproject.com?\n\n  " + list);
      if (!go) return;
      pubBtn.textContent = "Publishing…";
      showToast("Deploying to Cloudflare Pages…", false, 60000);
      return publishCall({}).then(function (d2) {
        if (!d2.ok) { publishFailed(d2); return; }
        showToast("Published " + (d2.changed || []).length +
                  " file(s) to alcuinproject.com. Cloudflare usually shows it within a minute.",
                  false, 8000);
      });
    }).catch(function () {
      showToast("Couldn't reach the edit server. Is it still running?", true);
    }).then(function () {
      pubBtn.disabled = false;
      pubBtn.textContent = "↑ Publish";
    });
  });

  saveBtn.addEventListener("click", function () { save(); });
  cancelBtn.addEventListener("click", function () { stopEditing(true); });

  document.addEventListener("keydown", function (e) {
    if (!active) return;
    if (e.key === "Escape") { e.preventDefault(); stopEditing(true); }
    if (e.key === "Enter" && (e.metaKey || e.ctrlKey)) { e.preventDefault(); save(); }
    // plain Enter inside a one-line block would insert a <div>; keep it flat
    if (e.key === "Enter" && !e.shiftKey) { e.preventDefault(); }
  });

  function pageSlug() {
    var p = window.location.pathname.split("/").pop();
    if (!p || p === "index.html") return "index";
    return p.replace(/\.html$/, "");
  }

  // ------------------------------------------- restore state after reload

  try {
    if (sessionStorage.getItem("al-editing") === "1") {
      sessionStorage.removeItem("al-editing");
      editing = true;
      document.body.classList.add("editing");
      btn.textContent = "✕ Done";
      markEditables(true);
      var where = sessionStorage.getItem("al-saved") || "";
      sessionStorage.removeItem("al-saved");
      showToast("Saved" + (where ? " to " + where : "") + ".");
    }
    var y = sessionStorage.getItem("al-scroll");
    if (y !== null) {
      sessionStorage.removeItem("al-scroll");
      window.scrollTo(0, parseInt(y, 10) || 0);
    }
  } catch (err) { /* ignore */ }
})();

"""Small static catalog; report content and private provenance stay separate."""

from __future__ import annotations

from html import escape
from urllib.parse import quote


def relative_url(record):
    parts = record["entrypoint"].split("/")
    if parts[-1] == "index.html":
        return record["report_id"] + "/" + "".join(quote(p, safe="") + "/" for p in parts[:-1])
    return record["report_id"] + "/" + "/".join(quote(p, safe="") for p in parts)


def render(records, enabled=True):
    rows = []
    if enabled:
        for record in sorted(records, key=lambda r: (r["created_at"], r["report_id"]), reverse=True):
            title = escape(record["title"])
            project = escape(record.get("project") or "")
            date = escape(record["created_at"])
            href = escape(relative_url(record), quote=True)
            rows.append(f'<li><a href="{href}">{title}</a><span>{project}</span><time>{date}</time></li>')
    content = ('<label>Find a report <input id="search" type="search" placeholder="Title or project"></label>'
               f'<p id="count">{len(rows)} reports</p><ul id="reports">' + "\n".join(rows) + "</ul>") if enabled else (
        "<p>Open a report using its direct link.</p>")
    script = """<script>
const search = document.querySelector('#search');
if (search) search.addEventListener('input', () => {
  const query = search.value.toLocaleLowerCase(); let shown = 0;
  document.querySelectorAll('#reports li').forEach(row => {
    row.hidden = !row.textContent.toLocaleLowerCase().includes(query); if (!row.hidden) shown++;
  }); document.querySelector('#count').textContent = shown + ' reports';
});
</script>"""
    return ("""<!doctype html><html lang="en"><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1"><title>Reports</title>
<style>
html{font:17px system-ui,sans-serif;color-scheme:light dark}body{max-width:900px;margin:3rem auto;padding:0 1rem}
h1{font-size:2rem}input{font:inherit;padding:.6rem;margin-left:.5rem;max-width:100%}
ul{list-style:none;padding:0}li{padding:1rem 0;border-bottom:1px solid #8885;display:grid;gap:.3rem}
li[hidden]{display:none}a{font-size:1.1rem}span,time{font-size:.85rem;opacity:.75}
</style><body><h1>Reports</h1>""" + content + script + "</body></html>\n").encode()

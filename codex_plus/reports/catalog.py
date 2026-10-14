"""Static project library; report content and private provenance stay separate."""

from __future__ import annotations

from collections import defaultdict
from datetime import datetime, timezone
from html import escape
from urllib.parse import quote


def relative_url(record):
    parts = record["entrypoint"].split("/")
    if parts[-1] == "index.html":
        return record["report_id"] + "/" + "".join(quote(p, safe="") + "/" for p in parts[:-1])
    return record["report_id"] + "/" + "/".join(quote(p, safe="") for p in parts)


def project_fragment(project):
    return "#project=" + quote(project, safe="") if project is not None else "#uncategorized=1"


def publication_label(value):
    try:
        date = datetime.fromisoformat(value)
        if date.tzinfo is not None:
            return date.astimezone(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    except ValueError:
        pass
    return value


SCRIPT = """<script>
const search = document.querySelector('#search');
const project = document.querySelector('#project');
if (search && project) {
  const groups = [...document.querySelectorAll('.project-group')];
  const count = document.querySelector('#count');
  const empty = document.querySelector('#empty');
  function filter() {
    const query = search.value.toLocaleLowerCase(); let shown = 0;
    groups.forEach(group => {
      const selected = !project.value || group.dataset.project === project.value;
      let matches = 0;
      group.querySelectorAll('li').forEach(row => {
        row.hidden = !selected || !row.dataset.search.toLocaleLowerCase().includes(query);
        if (!row.hidden) matches++;
      });
      group.hidden = !matches; shown += matches;
      group.querySelector('.group-count').textContent = matches + (matches === 1 ? ' report' : ' reports');
    });
    count.textContent = shown + (shown === 1 ? ' report' : ' reports');
    empty.hidden = shown !== 0;
  }
  function restore() {
    project.querySelectorAll('[data-missing]').forEach(option => option.remove());
    const params = new URLSearchParams(location.hash.slice(1));
    const selected = params.has('project') ? 'p:' + params.get('project') :
      params.get('uncategorized') === '1' ? 'u:' : '';
    const valid = [...project.options].some(option => option.value === selected);
    if (!valid) {
      const option = document.createElement('option');
      option.value = selected; option.dataset.missing = 'true';
      option.textContent = (selected === 'u:' ? 'Uncategorized (no project)' : params.get('project')) + ' (0)';
      project.append(option);
    }
    project.value = selected; search.value = params.get('search') || ''; filter();
  }
  function parameters() {
    const params = new URLSearchParams();
    if (project.value.startsWith('p:')) params.set('project', project.value.slice(2));
    else if (project.value === 'u:') params.set('uncategorized', '1');
    if (search.value) params.set('search', search.value);
    const fragment = params.toString();
    return location.pathname + location.search + (fragment ? '#' + fragment : '');
  }
  function remember() {
    history.replaceState(null, '', parameters()); filter();
  }
  search.addEventListener('input', remember);
  project.addEventListener('change', () => {
    history.pushState(null, '', parameters()); filter();
  });
  document.querySelector('#clear').addEventListener('click', () => {
    project.value = ''; search.value = ''; remember(); search.focus();
  });
  window.addEventListener('hashchange', restore);
  window.addEventListener('popstate', restore);
  restore();
}
</script>"""


def render(records, enabled=True):
    content = "<p>Open a report using its direct link.</p>"
    if enabled:
        groups = defaultdict(list)
        for record in sorted(records, key=lambda r: (r["created_at"], r["report_id"]), reverse=True):
            groups[record.get("project")].append(record)
        options = [f'<option value="">All projects ({len(records)})</option>']
        for project in sorted((p for p in groups if p is not None), key=lambda p: (p.casefold(), p)):
            options.append(f'<option value="{escape("p:" + project, quote=True)}">'
                           f'{escape(project)} ({len(groups[project])})</option>')
        if None in groups:
            options.append(f'<option value="u:">Uncategorized (no project) ({len(groups[None])})</option>')
        sections = []
        for number, (project, reports) in enumerate(groups.items()):
            label = project if project is not None else "Uncategorized (no project)"
            key = "p:" + project if project is not None else "u:"
            rows = []
            for record in reports:
                href = escape(relative_url(record), quote=True)
                title = escape(record["title"])
                date = escape(record["created_at"], quote=True)
                display_date = escape(publication_label(record["created_at"]))
                searchable = escape(record["title"] + " " + label, quote=True)
                rows.append(f'<li data-search="{searchable}"><a href="{href}">{title}</a>'
                            f'<time datetime="{date}">Published {display_date}</time></li>')
            count = str(len(rows)) + (" report" if len(rows) == 1 else " reports")
            sections.append(f'<section class="project-group" data-project="{escape(key, quote=True)}" '
                            f'aria-labelledby="project-{number}"><header><h2 id="project-{number}">'
                            f'<a href="{escape(project_fragment(project), quote=True)}">{escape(label)}</a></h2>'
                            f'<span class="group-count">{count}</span></header><ul>{"".join(rows)}</ul></section>')
        count = str(len(records)) + (" report" if len(records) == 1 else " reports")
        content = ('<p class="intro">Browse each project’s reports, newest first. Open reports in separate '
                   'browser tabs to compare earlier and later results.</p><div class="filters">'
                   '<label>Project <select id="project">' + "".join(options) + '</select></label>'
                   '<label>Find a report <input id="search" type="search" placeholder="Title or project"></label>'
                   '<button id="clear" type="button">Clear filters</button></div>'
                   f'<p id="count" role="status">{count}</p><p id="empty" hidden>No reports match these filters.</p>'
                   + "".join(sections))
    return ("""<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1"><title>Reports</title>
<style>
html{font:17px system-ui,sans-serif;color-scheme:light dark}body{max-width:1000px;margin:3rem auto;padding:0 1rem}
h1{font-size:2rem}.intro{line-height:1.6}.filters{display:flex;align-items:end;gap:1rem;flex-wrap:wrap}
label{display:grid;gap:.4rem}input,select,button{font:inherit;padding:.6rem;max-width:100%}
#count,.group-count,time{font-size:.85rem;opacity:.75}.project-group{margin:2rem 0}
header{display:flex;align-items:baseline;gap:1rem;flex-wrap:wrap}h2{font-size:1.3rem;margin:0}h2 a{text-decoration:none}
ul{list-style:none;padding:0}li{padding:1rem 0;border-bottom:1px solid #8885;display:grid;gap:.4rem}
[hidden]{display:none!important}li a{font-size:1.1rem}time{overflow-wrap:anywhere}
</style></head><body><main><h1>Reports</h1>""" + content + "</main>" + SCRIPT + "</body></html>\n").encode()

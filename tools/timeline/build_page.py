"""Build the timeline editor page for a project from work/timeline/timeline.json.
  python3 tools/timeline/build_page.py projects/<name> [--preview <asset url>] [--proxy <asset url>]
Media urls are remembered in work/timeline/media.json, so later builds only need the ones that changed.
Writes work/timeline/index.html, which is published as the project's artifact (see SKILL.md)."""
import argparse, json, os
ap = argparse.ArgumentParser()
ap.add_argument("project"); ap.add_argument("--preview"); ap.add_argument("--proxy")
a = ap.parse_args(); P = a.project.rstrip("/"); D = f"{P}/work/timeline"
T = json.load(open(f"{D}/timeline.json"))
mf = f"{D}/media.json"; media = json.load(open(mf)) if os.path.exists(mf) else {}
for k in ("preview", "proxy"):
    if getattr(a, k): media[k] = getattr(a, k)
json.dump(media, open(mf, "w"), indent=1)
T["media"] = {"preview": media.get("preview"), "proxy": media.get("proxy")}
tpl = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "editor.html")).read()
data = json.dumps(T, ensure_ascii=False, separators=(",", ":")).replace("<", "\\u003c")
html = tpl.replace("__TITLE__", f"{T['project']} Timeline").replace("__TIMELINE_JSON__", data)
open(f"{D}/index.html", "w").write(html)
print(f"{D}/index.html", len(html) // 1024, "KB", "preview" if T["media"]["preview"] else "-", "proxy" if T["media"]["proxy"] else "-")

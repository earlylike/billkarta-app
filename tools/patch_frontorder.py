#!/usr/bin/env python3
"""App-only, front page: no "Personal Selected" text; order Personal, Duty Manager, Senior Manager, My Notes."""
import os, re, sys
root = sys.argv[1]
fp = os.path.join(root, "frontpage", "index.html")
f = open(fp, encoding="utf-8").read()

# 1. remove the "<name> Selected" line (script keeps working with a detached element)
f = re.sub(r'\n\s*<div class="selected" id="selected"[^>]*>.*?</div>\n', '\n', f, flags=re.S)
f = f.replace("var selected = document.getElementById('selected');", "var selected = document.getElementById('selected') || document.createElement('div');")

# 2. order: My Notes card goes last
def block(name):
    m = re.search(r'        <button type="button" class="tab"[^>]*data-name="%s".*?</button>\n\n?' % re.escape(name), f, flags=re.S)
    assert m, name
    return m
pad, mom = block("My Notes"), block("Senior Manager")
if pad.start() < mom.start():
    pt = pad.group(0)
    f = f[:pad.start()] + f[pad.end():]
    mom = block("Senior Manager")
    mt = mom.group(0)
    f = f[:mom.start()] + mt.rstrip("\n") + "\n\n" + pt.rstrip("\n") + "\n\n" + f[mom.end():]
open(fp, "w", encoding="utf-8").write(f)
print("front order: patched")

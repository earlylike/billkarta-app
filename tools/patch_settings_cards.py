#!/usr/bin/env python3
"""App-only: on the Personal page, show Rates, Backup, Languages, Delete All Records and Trash
as separate cards inside Settings (like the Duty Manager page).
Usage: patch_settings_cards.py <assets/www folder>   (idempotent; run by sync-pages.sh)"""
import os, sys

p = os.path.join(sys.argv[1], "Work", "index.html")
s = open(p, encoding="utf-8").read()
if 'id="ratescard"' in s:
    print("settings cards already patched"); sys.exit(0)

def swap(old, new):
    global s
    assert s.count(old) == 1, (old, s.count(old))
    s = s.replace(old, new)

# The Settings wrapper stops being a card; each block becomes its own card.
swap('<section class="card" id="settings" aria-labelledby="sth">',
     '<section id="settings" aria-labelledby="sth">\n<div class="card" id="ratescard">')
swap('<div id="bkcard">', '</div>\n<div class="card" id="bkcard">')
swap('<div id="langcard">', '<div class="card" id="langcard">')
swap('<div id="dzcard">', '<div class="card" id="dzcard">')
swap('<div id="trashcard">', '<div class="card" id="trashcard">')

css = "\n/* BK-SETTINGS-CARDS */\n#settings .card{margin:0 0 1rem}\n#settings .card h2{margin-top:0}\n"
i = s.rfind("</style>")
assert i > 0
s = s[:i] + css + s[i:]
open(p, "w", encoding="utf-8").write(s)
print("patched Settings cards")

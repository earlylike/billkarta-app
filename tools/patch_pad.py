#!/usr/bin/env python3
"""App-only: adds BillKarta Pad (the notepad page from the earlylike/notepad repo) as a third card on the front page.
sync-pages.sh copies the page to assets/www/notepad; this script adds the card and locks the zoom like the other pages.
Usage: patch_pad.py <assets/www folder>   (idempotent)"""
import os, sys
MARK = "BK-PAD-CARD"
root = sys.argv[1]
fp = os.path.join(root, "frontpage", "index.html")
s = open(fp, encoding="utf-8").read()
if MARK not in s:
    anchor = '''        </button>

    </div>

    <div class="selected" id="selected"'''
    assert s.count(anchor) == 1
    card = '''        </button>

        <button type="button" class="tab" aria-pressed="false" data-name="BillKarta Pad" data-url="../notepad/index.html"><!-- BK-PAD-CARD -->
            <div class="tab-icon" aria-hidden="true">🗒️</div>
            <div class="tab-info">
                <h3>BillKarta Pad</h3>
                <p>Quick notes, saved on your phone</p>
            </div>
            <div class="arrow" aria-hidden="true">›</div>
        </button>

    </div>

    <div class="selected" id="selected"'''
    s = s.replace(anchor, card, 1)
    open(fp, "w", encoding="utf-8").write(s)
    print("front page: Pad card added")
else:
    print("front page: Pad card already added")
np = os.path.join(root, "notepad", "index.html")
if os.path.exists(np):
    t = open(np, encoding="utf-8").read()
    a = 'name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover"'
    b = 'name="viewport" content="width=device-width, initial-scale=1, minimum-scale=1, maximum-scale=1, user-scalable=no, viewport-fit=cover"'
    if a in t:
        open(np, "w", encoding="utf-8").write(t.replace(a, b, 1)); print("pad: zoom locked")

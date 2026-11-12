#!/usr/bin/env python3
"""App-only TRIAL: pastel-panel cards (white frame + soft tinted panel) on the Personal and Duty Manager pages.
To remove: revert the git commit that added this file (it also removes the call from sync-pages.sh).
Usage: patch_card_colors.py <assets/www folder>   (idempotent; run by sync-pages.sh)"""
import os, sys

MARK = "BK-CARD-COLORS"

BASE = """
/* BK-CARD-COLORS */
.card{--tint:#e4defc;background:var(--tint);background-clip:padding-box;border:7px solid var(--card);
  border-radius:26px;box-shadow:var(--shadow)}
@media (prefers-color-scheme:dark){.card{background:color-mix(in srgb,var(--tint) 17%,var(--card));background-clip:padding-box}}
.card input:not([type=radio]):not([type=checkbox]):not([type=file]):not([type=range]),.card select,.card textarea{background:var(--card)}
"""

TINTS = {
    "work": """
.card[aria-labelledby="addh"]{--tint:#c8f3dc}
.card[aria-label="Summary"]{--tint:#e4defc}
.card[aria-labelledby="listh"]{--tint:#d3ebfb}
#adv.card{--tint:#fde3cf}
.card[aria-label="Bill"]{--tint:#fdf1c2}
.card[aria-labelledby="wah"]{--tint:#c8f3dc}
#ratescard{--tint:#fde3cf}
#bkcard{--tint:#d3ebfb}
#langcard{--tint:#e4defc}
#dzcard{--tint:#fbd9e3}
#trashcard{--tint:#fbd9e3}
""",
    "forall": """
.card:has(#addh){--tint:#c8f3dc}
.card:has(#list){--tint:#d3ebfb}
#bill.card{--tint:#fdf1c2}
#details.card{--tint:#e4defc}
.card:has(#rfull){--tint:#fde3cf}
.card:has(#emps){--tint:#c8f3dc}
#trashcard{--tint:#fbd9e3}
#bkcard{--tint:#d3ebfb}
#langcard{--tint:#e4defc}
.card:has(#acount){--tint:#fde3cf}
""",
}

for page, key in (("Work", "work"), ("forall", "forall")):
    p = os.path.join(sys.argv[1], page, "index.html")
    s = open(p, encoding="utf-8").read()
    if MARK in s:
        print(page, "card colors already patched"); continue
    i = s.rfind("</style>")
    assert i > 0
    s = s[:i] + BASE + TINTS[key] + s[i:]
    open(p, "w", encoding="utf-8").write(s)
    print("patched card colors:", page)

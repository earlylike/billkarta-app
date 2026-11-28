#!/usr/bin/env python3
"""Personal, Duty Manager, Senior Manager: adds WhatsApp + Instagram buttons (with small logos, embedded so they work offline)
to the 'Privacy & Contact' card. Run last."""
import base64, os, sys
from urllib.parse import quote
root = sys.argv[1]
here = os.path.dirname(os.path.abspath(__file__))
b64 = lambda n: base64.b64encode(open(os.path.join(here, "assets", n), "rb").read()).decode()
WA = "https://wa.me/919822268544?text=" + quote("Hello BillKarta, I have a question about the app.")
IG = "https://www.instagram.com/billkarta/"
CSS = "<style>/* BK-SOCIAL */#aboutcard .about-actions a.soc{display:flex;align-items:center;justify-content:center;gap:.5rem;height:50px;padding:0;box-sizing:border-box}#aboutcard .about-actions a.soc img{width:20px;height:20px;display:block}</style>"
BTNS = ('<a class="soc" href="%s" rel="noopener"><img src="data:image/png;base64,%s" alt="" width="20" height="20">WhatsApp</a>'
        '<a class="soc" href="%s" rel="noopener"><img src="data:image/png;base64,%s" alt="" width="20" height="20">Instagram</a>') % (WA, b64("wa.png"), IG, b64("ig.png"))
for page in ["Work", "forall", "mom"]:
    fp = os.path.join(root, page, "index.html")
    f = open(fp, encoding="utf-8").read()
    if "BK-SOCIAL" in f:
        print("social: %s already patched" % page); continue
    i = f.index('id="aboutcard"'); j = f.index('class="about-actions"', i); k = f.index("</div>", j)
    f = f[:k] + BTNS + f[k:]
    assert f.count("</head>") >= 1
    f = f.replace("</head>", CSS + "</head>", 1)
    open(fp, "w", encoding="utf-8").write(f)
    print("social: %s patched" % page)

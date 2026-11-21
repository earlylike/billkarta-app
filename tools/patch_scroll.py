#!/usr/bin/env python3
"""App-only: on the Duty Manager Duty tab, tapping "All employees details" smoothly glides the page down so
the opened details are in view (like after adding an entry). Closing does not scroll.
Usage: patch_scroll.py <assets/www folder>   (idempotent; run by sync-pages.sh)"""
import os, sys
MARK = "BK-DETAILS-SCROLL"
p = os.path.join(sys.argv[1], "forall", "index.html")
s = open(p, encoding="utf-8").read()
if MARK in s:
    print("details scroll already patched"); sys.exit(0)
CSS = "<style>/* BK-DETAILS-SCROLL */#details{scroll-margin-top:96px}</style>"
JS = """<script>/* BK-DETAILS-SCROLL */(function(){
  var t=document.getElementById('dtoggle');if(!t)return;
  t.addEventListener('click',function(){
    if(t.getAttribute('aria-expanded')!=='true')return;
    setTimeout(function(){
      var d=document.getElementById('details');if(!d)return;
      var calm=window.matchMedia&&window.matchMedia('(prefers-reduced-motion: reduce)').matches;
      d.scrollIntoView({behavior:calm?'auto':'smooth',block:'start'});
    },120);
  });
})();</script>"""
assert s.count("</head>") == 1
s = s.replace("</head>", CSS + "</head>", 1)
i = s.rfind("</body>")
s = s[:i] + JS + "\n" + s[i:]
open(p, "w", encoding="utf-8").write(s)
print("patched details scroll")

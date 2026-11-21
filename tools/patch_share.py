#!/usr/bin/env python3
"""App-only: small share icon (top right of the first page). Tapping it opens the phone's share sheet
with a short message and the Play Store link. Needs the native AndroidBridge.shareApp method.
Usage: patch_share.py <assets/www folder>   (idempotent; run by sync-pages.sh)"""
import os, sys
MARK = "BK-SHARE"
p = os.path.join(sys.argv[1], "frontpage", "index.html")
s = open(p, encoding="utf-8").read()
if MARK in s:
    print("share already patched"); sys.exit(0)
CSS = """<style>/* BK-SHARE */
.bk-share{position:fixed;top:12px;right:12px;z-index:20;width:29px;height:29px;padding:0;border-radius:50%;display:grid;place-items:center;
  border:1px solid rgba(198,156,80,.6);background:rgba(8,10,14,.78);box-shadow:0 8px 24px rgba(0,0,0,.45);cursor:pointer;-webkit-tap-highlight-color:transparent}
.bk-share svg{width:12px;height:12px;fill:none;stroke:#f4d58d;stroke-width:2.2;stroke-linecap:round;stroke-linejoin:round}
.bk-share::after{content:"";position:absolute;inset:-8px}
</style>"""
BTN = ('<button type="button" class="bk-share" id="bkShare" aria-label="Share BillKarta">'
       '<svg viewBox="0 0 24 24" aria-hidden="true"><circle cx="18" cy="5" r="2.6"/><circle cx="6" cy="12" r="2.6"/><circle cx="18" cy="19" r="2.6"/>'
       '<path d="M8.3 10.8l7.4-4.3M8.3 13.2l7.4 4.3"/></svg></button>\n')
JS = """<script>/* BK-SHARE */(function(){
  var MSG='Try BillKarta, a free app to record work duties and make bills. It works offline: https://play.google.com/store/apps/details?id=com.earlylike.billkarta';
  var b=document.getElementById('bkShare');if(!b)return;
  b.addEventListener('click',function(){
    try{if(window.AndroidBridge&&AndroidBridge.shareApp){AndroidBridge.shareApp(MSG);return;}}catch(e){}
    try{if(navigator.share){navigator.share({text:MSG});return;}}catch(e){}
  });
})();</script>"""
assert s.count("</body>") == 1 and s.count("</head>") == 1
s = s.replace("</head>", CSS + "</head>", 1)
i = s.rfind("</body>")
s = s[:i] + BTN + JS + "\n" + s[i:]
open(p, "w", encoding="utf-8").write(s)
print("patched share icon")

#!/usr/bin/env python3
"""App-only: adds the diagonal gold word-pattern background to the front (landing) page.
Usage: patch_frontpage_bg.py <assets/www folder>   (idempotent; run by sync-pages.sh)"""
import os, sys

MARK = "BK-WORD-BG"
p = os.path.join(sys.argv[1], "frontpage", "index.html")
s = open(p, encoding="utf-8").read()
if MARK in s:
    print("frontpage background already patched"); sys.exit(0)

CSS = """
/* BK-WORD-BG */
.bg-words{position:fixed;left:-35%;right:-35%;top:-25%;bottom:-25%;z-index:0;pointer-events:none;overflow:hidden;
  transform:rotate(-18deg);display:flex;flex-direction:column;justify-content:center;gap:.72rem;
  font-weight:800;text-transform:uppercase;letter-spacing:.02em;font-size:1.1rem;line-height:1.1;white-space:nowrap;
  color:rgba(218,177,91,.17);-webkit-mask-image:linear-gradient(to bottom,transparent 0,#000 14%,#000 86%,transparent 100%);
  mask-image:linear-gradient(to bottom,transparent 0,#000 14%,#000 86%,transparent 100%)}
.bg-words .row{display:block}
.bg-words .row:nth-child(3n+1){color:rgba(218,177,91,.2)}
.bg-words .row:nth-child(3n+2){color:rgba(218,177,91,.12)}
.bg-glow{position:fixed;inset:0;z-index:0;pointer-events:none;
  background:radial-gradient(120% 60% at 100% 0%,rgba(218,160,40,.34),transparent 60%),
             radial-gradient(90% 50% at 0% 100%,rgba(218,160,40,.16),transparent 60%)}
.container{position:relative;z-index:1;background:rgba(14,15,18,.72);-webkit-backdrop-filter:blur(2px);backdrop-filter:blur(2px)}
"""

JS = """<div class="bg-glow" aria-hidden="true"></div><div class="bg-words" id="bgwords" aria-hidden="true"></div>
<script>
/* BK-WORD-BG */
(function(){
  var words=['Workers','Employees','Employers','Contractors','Managers','Labourers','Caterers'];
  var host=document.getElementById('bgwords');if(!host)return;
  var rows=46,html='';
  for(var r=0;r<rows;r++){
    var line='';
    for(var k=0;k<24;k++){line+=words[(r*3+k)%words.length]+' \\u2022 ';}
    html+='<span class="row" style="margin-left:'+(-(r%4)*7)+'%">'+line+'</span>';
  }
  host.innerHTML=html;
})();
</script>
"""

i = s.rfind("</style>")
j = s.find("<body")
assert i > 0 and j > 0
k = s.find(">", j) + 1
s = s[:i] + CSS + s[i:]
k = s.find(">", s.find("<body")) + 1
s = s[:k] + "\n" + JS + s[k:]
open(p, "w", encoding="utf-8").write(s)
print("patched frontpage background")

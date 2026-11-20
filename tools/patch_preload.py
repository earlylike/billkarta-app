#!/usr/bin/env python3
"""App-only TRIAL: after the first page has drawn, quietly preload the Personal (Work) and Duty Manager (forall)
pages in hidden frames, one after the other, so opening them later feels faster.
To remove: revert the git commit that added this file (it also removes the call from sync-pages.sh).
Usage: patch_preload.py <assets/www folder>   (idempotent; run by sync-pages.sh)"""
import os, sys

MARK = "BK-PRELOAD"
p = os.path.join(sys.argv[1], "frontpage", "index.html")
s = open(p, encoding="utf-8").read()
if MARK in s:
    print("preload already patched"); sys.exit(0)

JS = """<script>/* BK-PRELOAD */
(function(){
  var urls=['../Work/index.html','../forall/index.html'],i=0,started=false;
  function next(){
    if(i>=urls.length)return;
    var f=document.createElement('iframe');
    f.setAttribute('aria-hidden','true');f.tabIndex=-1;f.src=urls[i++];
    f.style.cssText='position:absolute;width:1px;height:1px;border:0;opacity:0;pointer-events:none;left:-9999px;top:0';
    f.onload=function(){setTimeout(next,600);};
    document.body.appendChild(f);
  }
  function start(){if(started)return;started=true;setTimeout(next,500);}
  function idle(){(window.requestIdleCallback?requestIdleCallback(start,{timeout:1500}):setTimeout(start,300));}
  if(document.readyState==='complete')idle();else window.addEventListener('load',idle);
})();
</script>"""
i = s.rfind("</body>")
assert i > 0
s = s[:i] + JS + "\n" + s[i:]
open(p, "w", encoding="utf-8").write(s)
print("patched frontpage preload")

#!/usr/bin/env python3
"""App-only: live counter (round purple-pink badge) next to "Who did the duty" on the Duty Manager page,
for both the Add Duty form and the Edit Duty window. Website repos are never changed.
Usage: patch_count.py <assets/www folder>   (idempotent; run by sync-pages.sh)"""
import os, sys
MARK = "BK-COUNT"
p = os.path.join(sys.argv[1], "forall", "index.html")
s = open(p, encoding="utf-8").read()
if MARK in s:
    print("count already patched"); sys.exit(0)
CSS = """<style>/* BK-COUNT */
#wl,#ewl{display:inline-block}
.bk-n{display:inline-block;vertical-align:middle;min-width:22px;height:22px;padding:0 6px;margin-left:.5rem;border-radius:99px;text-align:center;
  font:800 .78rem/22px 'Poppins',system-ui,sans-serif;color:#fff;background:linear-gradient(135deg,#ec4899,#7c3aed);box-shadow:0 2px 7px rgba(124,58,237,.4)}
.bk-n[hidden]{display:none}
.bk-n.pop{animation:bkPop .2s ease-out}
@keyframes bkPop{0%{transform:scale(.8)}60%{transform:scale(1.12)}100%{transform:scale(1)}}
@media (prefers-reduced-motion:reduce){.bk-n.pop{animation:none}}
</style>"""
JS = """<script>/* BK-COUNT */(function(){
  function wire(labelId,boxId){
    var lab=document.getElementById(labelId),box=document.getElementById(boxId);if(!lab||!box)return null;
    var b=document.createElement('span');b.className='bk-n';b.hidden=true;b.setAttribute('aria-live','polite');lab.parentNode.insertBefore(b,lab.nextSibling);
    var last=0;
    function upd(){
      var n=box.querySelectorAll('input:checked').length;
      if(n===last)return;last=n;
      if(n===0){b.hidden=true;return;}
      b.hidden=false;b.textContent=n;b.classList.remove('pop');void b.offsetWidth;b.classList.add('pop');
    }
    box.addEventListener('change',upd);
    new MutationObserver(upd).observe(box,{childList:true});
    return upd;
  }
  function init(){
    var a=wire('wl','who'),e=wire('ewl','ewho'),save=document.getElementById('save');
    if(save&&a)save.addEventListener('click',function(){setTimeout(a,0);a();});
    /* the page can come back from the PDF editor with the ticks restored by the browser (no change event),
       so also re-check on pageshow and with a very light timer while the page is visible */
    function all(){if(a)a();if(e)e();}
    window.addEventListener('pageshow',function(){all();setTimeout(all,150);});
    document.addEventListener('visibilitychange',function(){if(!document.hidden)all();});
    setInterval(function(){if(!document.hidden)all();},400);
    all();
  }
  if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',init);else init();
})();</script>"""
assert "</head>" in s and "</body>" in s
s = s.replace("</head>", CSS + "</head>", 1)
i = s.rfind("</body>")
s = s[:i] + JS + "\n" + s[i:]
open(p, "w", encoding="utf-8").write(s)
print("patched Duty Manager counter")

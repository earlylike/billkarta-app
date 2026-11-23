#!/usr/bin/env python3
"""App-only: My Notes (notepad page) gets the same gold BillKarta header (stars, twinkles) and the same gold tabs with
the sliding plate as the Personal / Duty Manager pages. Header and tabs are copied from the patched Duty Manager page,
so run this AFTER patch_header.py. The Sort box moves into the header, the tabs move from the bottom to under the header.
Usage: patch_padhead.py <assets/www folder>   (idempotent)"""
import os, re, sys
MARK = "BK-PAD-HEAD"
root = sys.argv[1]
fa = open(os.path.join(root, "forall", "index.html"), encoding="utf-8").read()
fp = os.path.join(root, "notepad", "index.html")
s = open(fp, encoding="utf-8").read()
if MARK in s:
    print("padhead: already patched"); sys.exit(0)
hero = re.search(r'<header class="hero">.*?</header>', fa, re.S).group(0)
css = re.search(r'<style>\s*/\* BK-GOLD-HEADER \*/.*?</style>', fa, re.S).group(0)
OVR = """<style>/* BK-PAD-HEAD */
.home{overflow:hidden}
.hero h1.brand{display:block !important}
.home nav[role="tablist"]{position:relative !important;margin:8px 14px 10px !important;top:auto !important;border-radius:22px;overflow:hidden}
.home nav[role="tablist"] button{pointer-events:auto !important;position:relative !important;flex-direction:row !important;font-size:14px !important;padding:0 6px !important;height:auto !important;background:none !important;box-shadow:none !important;gap:.4rem !important}
.home nav[role="tablist"] button::after{display:none !important}
.home nav[role="tablist"] button svg{pointer-events:none !important;width:20px !important;height:20px !important;padding:0 !important;margin:0 !important;background:none !important;box-shadow:none !important;transform:none !important;border-radius:0 !important;color:inherit !important;touch-action:manipulation}
.home nav[role="tablist"] button.on{color:#1a1405 !important}
#sort{position:absolute;right:10px;top:50%;transform:translateY(-50%);z-index:3;pointer-events:auto;font-size:11px;padding:3px 6px;border-radius:12px;background:rgba(255,255,255,.18);color:#fff;border:1px solid rgba(255,255,255,.4);max-width:110px}
#sort option{color:#111}
</style>"""
SCRIPT = """<script>/* BK-PAD-HEAD */(function(){
function init(){
  var home=document.querySelector('.home'),hero=home&&home.querySelector('.hero'),nav=home&&home.querySelector('nav.nav'),sort=document.getElementById('sort');
  if(!hero||!nav)return;
  var hin=hero.querySelector('.hero-in')||hero;if(sort)hin.appendChild(sort);
  hero.parentNode.insertBefore(nav,hero.nextSibling);
  nav.setAttribute('role','tablist');
  var plate=document.createElement('span');plate.className='bk-plate';plate.setAttribute('aria-hidden','true');nav.insertBefore(plate,nav.firstChild);
  var btns=nav.querySelectorAll('button');
  function place(){
    var on=null;btns.forEach(function(b){b.setAttribute('role','tab');var o=b.classList.contains('on');b.setAttribute('aria-selected',o?'true':'false');if(o)on=b;var sv=b.querySelector('svg');if(sv&&!sv.classList.contains('bk-ic'))sv.classList.add('bk-ic');});
    if(!on)return;plate.style.width=on.offsetWidth+'px';plate.style.transform='translateX('+on.offsetLeft+'px)';
  }
  new MutationObserver(place).observe(nav,{attributes:true,subtree:true,attributeFilter:['class']});
  window.addEventListener('resize',place);
  if(document.fonts&&document.fonts.ready)document.fonts.ready.then(place);
  place();setTimeout(place,150);
}
if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',init);else init();
})();</script>"""
s, n = re.subn(r'<header class="top">.*?</header>', lambda m: hero.replace('</header>', '</header>'), s, count=1, flags=re.S)
assert n == 1
# the sort <select> was inside the old header: re-add it so it can be moved into the hero
s = s.replace(hero, hero + '\n<select id="sort" aria-label="Sort notes"><option value="t">Modified</option><option value="c0">Created</option><option value="a">Title A–Z</option><option value="c">Color</option></select>', 1)
s = s.replace("</head>", css + OVR + "</head>", 1)
s = s.replace("</body>", SCRIPT + "</body>", 1)
open(fp, "w", encoding="utf-8").write(s)
print("padhead: patched")

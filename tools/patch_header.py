#!/usr/bin/env python3
"""App-only TRIAL: short gold header (stars, twinkles) + decorated equal-size tabs with a sliding gold plate
and a smooth fade/slide when switching tabs, on the Personal (Work) and Duty Manager (forall) pages.
To remove: revert the git commit that added this file (it also removes the call from sync-pages.sh).
Usage: patch_header.py <assets/www folder>   (idempotent; run by sync-pages.sh)"""
import os, re, sys

MARK = "BK-GOLD-HEADER"

STARS = ('<span class="orb" aria-hidden="true"></span>'
  + ''.join('<span aria-hidden="true" class="cr k%d%s"><i></i></span>' % (n, ' rev' if r else '')
            for n, r in [(1,0),(2,1),(3,0),(4,1),(5,0),(10,1)]))
TW = ''.join('<span class="tw" style="left:%s;top:%s;--z:%s;--p:%s;--q:%s" aria-hidden="true"></span>' % t
  for t in [("8%","14px","2px","3.1s","0s"),("18%","44px","1.5px","2.6s","0.8s"),("27%","22px","2px","3.6s","1.4s"),
            ("36%","50px","1.5px","2.9s","0.3s"),("45%","10px","2px","3.3s","2s")])

CSS = """
/* BK-GOLD-HEADER */
.hero,.hero *{box-sizing:border-box}
.hero{position:sticky;overflow:visible;color:#fff;z-index:50;pointer-events:none;background:none !important;box-shadow:none !important;
  padding:calc(.55rem + env(safe-area-inset-top,0px)) .9rem 1.5rem !important;border-radius:0 !important}
.hero-bg{position:absolute;inset:0;overflow:hidden;z-index:-1;pointer-events:none;border-radius:0 0 28px 28px;
  background:radial-gradient(60% 90% at 92% 0%,rgba(255,214,120,.55),transparent 65%),
    radial-gradient(60% 90% at 2% 20%,rgba(198,156,80,.30),transparent 65%),
    linear-gradient(165deg,#0c0d12 0%,#2b2111 52%,#8a6420 100%);
  box-shadow:0 10px 26px rgba(184,137,53,.28);will-change:opacity,transform}
.hero .orb{position:absolute;border-radius:50%;pointer-events:none;filter:blur(18px);opacity:.8;width:150px;height:150px;right:6%;top:-40px;
  background:radial-gradient(circle,#f5d990,transparent 68%)}
.hero-in{position:relative;z-index:1;max-width:40rem;margin:0 auto;padding:.6rem .8rem !important;background:none !important;border:0 !important;box-shadow:none !important}
.hero-in .glass{position:absolute;inset:0;z-index:0;border-radius:18px;overflow:hidden;pointer-events:none;
  background:linear-gradient(135deg,rgba(255,255,255,.22),rgba(255,255,255,.07));border:1px solid rgba(245,217,144,.38);
  -webkit-backdrop-filter:blur(14px) saturate(1.5);backdrop-filter:blur(14px) saturate(1.5);
  box-shadow:0 12px 30px rgba(0,0,0,.45),inset 0 1px 0 rgba(255,235,190,.45);will-change:opacity,transform}
.hero-in .glass::after{content:"";position:absolute;inset:0;border-radius:inherit;pointer-events:none;
  background:linear-gradient(105deg,transparent 38%,rgba(255,255,255,.30) 50%,transparent 62%) 220% 0/260% 100% no-repeat;animation:bkShine 6s ease-in-out 1.2s infinite}
@keyframes bkShine{0%{background-position:220% 0}55%,100%{background-position:-120% 0}}
.bk-chip{position:absolute;z-index:0;left:0;top:0;border-radius:999px;pointer-events:none;opacity:0;background:rgba(18,14,8,.92);
  border:1px solid rgba(245,217,144,.35);box-shadow:0 6px 16px rgba(16,12,4,.3)}
.hero h1.brand{position:relative;z-index:2;line-height:0;margin:0;transform-origin:left center;will-change:transform}
.hero h1.brand img{display:block;margin:0 auto;height:24px !important;width:auto;max-width:68% !important;filter:drop-shadow(0 2px 10px rgba(40,10,60,.5))}
.hero .cr{position:absolute;left:-24px;pointer-events:none;z-index:0;opacity:0;
  filter:drop-shadow(0 0 3px rgba(255,255,255,.9)) drop-shadow(0 0 7px rgba(255,200,120,.6));animation:bkCrR var(--t,16s) linear var(--d,0s) infinite}
.hero .cr.rev{left:auto;right:-24px;animation-name:bkCrL}
.hero .cr i{display:block;width:calc(var(--s,10px)*.75);height:calc(var(--s,10px)*.75);position:relative;
  clip-path:polygon(50% 0,61% 35%,98% 35%,68% 57%,79% 91%,50% 70%,21% 91%,32% 57%,2% 35%,39% 35%);
  background:linear-gradient(125deg,#fff 0%,#fff1c2 50%,#fff 100%);animation:bkCrW var(--w,5s) ease-in-out var(--d,0s) infinite alternate}
.hero .cr i::after{content:"";position:absolute;inset:0;background:#fff;animation:bkGlint var(--w,5s) ease-in-out infinite alternate}
@keyframes bkCrR{0%{opacity:0;transform:translateX(0)}8%{opacity:1}92%{opacity:1}100%{opacity:0;transform:translateX(calc(100vw + 48px))}}
@keyframes bkCrL{0%{opacity:0;transform:translateX(0)}8%{opacity:1}92%{opacity:1}100%{opacity:0;transform:translateX(calc(-100vw - 48px))}}
@keyframes bkCrW{0%{transform:translateY(calc(var(--a,14px)*-1)) rotate(-18deg)}100%{transform:translateY(var(--a,14px)) rotate(18deg)}}
@keyframes bkGlint{0%,100%{opacity:0}50%{opacity:.9}}
.hero .k1{top:14px;--s:11px;--t:17s;--w:4.6s;--a:10px;--d:-2s}
.hero .k2{top:34px;--s:8px;--t:21s;--w:5.8s;--a:8px;--d:-9s}
.hero .k3{top:50px;--s:13px;--t:19s;--w:6.4s;--a:8px;--d:-5s}
.hero .k4{top:24px;--s:9px;--t:23s;--w:5.2s;--a:10px;--d:-14s}
.hero .k5{top:44px;--s:7px;--t:15s;--w:4.2s;--a:7px;--d:-7s}
.hero .k10{top:30px;--s:12px;--t:12s;--w:4.6s;--a:9px;--d:-3s}
.hero .tw{position:absolute;width:var(--z,2px);height:var(--z,2px);border-radius:50%;pointer-events:none;z-index:0;background:#fff;
  box-shadow:0 0 5px 1px rgba(255,255,255,.8);opacity:.15;animation:bkTwk var(--p,3s) ease-in-out var(--q,0s) infinite}
@keyframes bkTwk{0%,100%{opacity:.12;transform:scale(.7)}50%{opacity:1;transform:scale(1.5)}}
main,.wrap{margin-top:-.45rem !important}
/* warm cream page background to match the gold header */
:root{--bg:#fbf4e4 !important}
body{background:linear-gradient(180deg,#fbf4e4 0%,#f7edd2 100%) fixed !important}
@media (prefers-color-scheme:dark){:root{--bg:#14110a !important}body{background:linear-gradient(180deg,#17130b 0%,#0f0c07 100%) fixed !important}}
/* tabs: three equal-size buttons with icons and a sliding gold plate */
.tabs,nav[role="tablist"]{position:sticky;display:flex !important;gap:.3rem !important;padding:.3rem !important;box-sizing:border-box;
  border-radius:20px;background:rgba(18,14,8,.9) !important;border:1px solid rgba(245,217,144,.30);
  box-shadow:0 8px 22px rgba(16,12,4,.28),inset 0 1px 0 rgba(255,235,190,.16);isolation:isolate}
.tab,nav[role="tablist"] button{position:relative;z-index:1;flex:1 1 0 !important;min-width:0;min-height:44px;display:flex;align-items:center;justify-content:center;gap:.4rem;
  padding:.55rem .2rem !important;border:0 !important;border-radius:15px !important;background:transparent !important;box-shadow:none !important;
  color:rgba(245,226,176,.85) !important;font:inherit;font-weight:600;font-size:.9rem;cursor:pointer;transition:color .3s,transform .15s}
.tab:active,nav[role="tablist"] button:active{transform:scale(.96)}
.tab.on,nav[role="tablist"] button[aria-selected="true"]{color:#1a1405 !important;background:transparent !important}
.bk-ic{width:18px;height:18px;flex:none;fill:none;stroke:currentColor;stroke-width:1.8;stroke-linecap:round;stroke-linejoin:round}
.bk-plate{position:absolute;z-index:0;top:.3rem;bottom:.3rem;left:0;width:0;border-radius:15px;pointer-events:none;
  background:linear-gradient(135deg,#f5d990 0%,#d9b062 48%,#b8893a 100%);
  box-shadow:0 6px 16px rgba(198,156,80,.38),inset 0 1px 0 rgba(255,255,255,.6),inset 0 -1px 0 rgba(120,80,10,.35);
  transition:transform .42s cubic-bezier(.3,1.25,.4,1),width .42s cubic-bezier(.3,1.25,.4,1)}
/* smooth content change when switching tabs (restarts each time a panel becomes visible) */
main>section,main>#adv,#p-duty,#p-adv,#p-set{animation:bkIn .4s cubic-bezier(.2,.8,.2,1)}
@keyframes bkIn{from{opacity:0;transform:translateY(14px)}to{opacity:1;transform:none}}
@media (prefers-reduced-motion:reduce){.hero .cr,.hero .tw,.glass::after{display:none}.bk-plate,main>section,main>#adv,#p-duty,#p-adv,#p-set{animation:none;transition:none}}
"""

ICONS = {
 "duty": '<svg class="bk-ic" viewBox="0 0 24 24" aria-hidden="true"><rect x="3.5" y="5" width="17" height="15.5" rx="3"/><path d="M3.5 10h17M8 3v4M16 3v4M9 15l2.2 2.2L15.5 13"/></svg>',
 "adv": '<svg class="bk-ic" viewBox="0 0 24 24" aria-hidden="true"><path d="M4 7.5A2.5 2.5 0 0 1 6.5 5H18a2 2 0 0 1 2 2v2"/><path d="M4 7.5V17a2.5 2.5 0 0 0 2.5 2.5H19a1 1 0 0 0 1-1V10a1 1 0 0 0-1-1H6.5A2.5 2.5 0 0 1 4 7.5Z"/><circle cx="16" cy="14.2" r="1.1"/></svg>',
 "set": '<svg class="bk-ic" viewBox="0 0 24 24" aria-hidden="true"><path d="M4 7h9M17 7h3M4 17h3M11 17h9"/><circle cx="15" cy="7" r="2"/><circle cx="9" cy="17" r="2"/></svg>',
}

JS = """<script>/* BK-GOLD-HEADER */(function(){
function init(){
  var nav=document.querySelector('nav.tabs,nav[role="tablist"]');if(!nav)return;
  var plate=document.createElement('span');plate.className='bk-plate';plate.setAttribute('aria-hidden','true');nav.insertBefore(plate,nav.firstChild);
  function place(){
    var on=nav.querySelector('button.on,button[aria-selected="true"]');if(!on)return;
    plate.style.width=on.offsetWidth+'px';plate.style.transform='translateX('+on.offsetLeft+'px)';
  }
  new MutationObserver(place).observe(nav,{attributes:true,subtree:true,attributeFilter:['class','aria-selected','aria-pressed']});
  window.addEventListener('resize',place);
  if(document.fonts&&document.fonts.ready)document.fonts.ready.then(place);
  place();setTimeout(place,150);

  var hero=document.querySelector('.hero');
  if(hero){
    var h1=hero.querySelector('h1.brand'),img=h1&&h1.querySelector('img'),glass=hero.querySelector('.glass'),bg=hero.querySelector('.hero-bg'),chip=hero.querySelector('.bk-chip');
    var probe=document.createElement('div');probe.style.cssText='position:absolute;visibility:hidden;padding-top:env(safe-area-inset-top,0px)';document.body.appendChild(probe);
    var M={};
    function measure(){
      h1.style.transform='';var safe=parseFloat(getComputedStyle(probe).paddingTop)||0;
      var BAR=safe+42,H=hero.offsetHeight,R=Math.max(1,H-BAR);
      hero.style.top=(-R)+'px';nav.style.top=(BAR+6)+'px';
      var hr=hero.getBoundingClientRect(),ir=img.getBoundingClientRect(),sc=.8;
      M={R:R,ty:safe+21-(ir.top-hr.top+ir.height/2)-0,tx:14-(ir.left),sc:sc,w:ir.width*sc,h:ir.height*sc,top:safe+21};
      var hl=h1.getBoundingClientRect().left;M.tx=14-hl-(ir.left-hl)*sc;
      chip.style.width=(M.w+24)+'px';chip.style.height=(M.h+16)+'px';
      frame();
    }
    var tick=false;
    function frame(){
      tick=false;if(!M.R)return;
      var sy=Math.max(0,window.pageYOffset||document.documentElement.scrollTop||0),s=Math.min(sy,M.R),p=s/M.R;
      h1.style.transform='translate('+(M.tx*p)+'px,'+(s+M.ty*p)+'px) scale('+(1-(1-M.sc)*p)+')';
      glass.style.transform='translateX('+(-p*115)+'%)';glass.style.opacity=Math.max(0,1-p*1.15);
      bg.style.opacity=Math.max(0,1-p*1.2);bg.style.transform='translateY('+(-p*20)+'px)';
      var co=Math.max(0,(p-.6)/.4);chip.style.opacity=co;
      chip.style.transform='translate('+(14-12)+'px,'+(M.top-(M.h+16)/2+s)+'px)';
    }
    window.addEventListener('scroll',function(){if(!tick){tick=true;requestAnimationFrame(frame);}},{passive:true});
    window.addEventListener('resize',measure);
    if(document.fonts&&document.fonts.ready)document.fonts.ready.then(measure);
    if(img&&!img.complete)img.addEventListener('load',measure);
    measure();setTimeout(measure,200);
  }
}
if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',init);else init();
})();</script>"""

def patch(path):
    s = open(path, encoding="utf-8").read()
    if MARK in s:
        return False
    # header: keep the existing logo <h1>, rebuild the rest
    m = re.search(r'<header class="hero">(.*?)</header>', s, re.S)
    assert m, path
    h1 = re.search(r'<h1 class="brand">.*?</h1>', m.group(1), re.S)
    assert h1, path
    new = ('<header class="hero"><div class="hero-bg">' + STARS + TW + '</div><span class="bk-chip" aria-hidden="true"></span>'
           '<div class="hero-in"><span class="glass" aria-hidden="true"></span>' + h1.group(0) + '</div></header>')
    s = s[:m.start()] + new + s[m.end():]
    # tab icons
    def icon(mo):
        key = mo.group(2)
        open_tag = mo.group(1)
        di = re.search(r' data-i18n="[^"]*"', open_tag)
        attr = di.group(0) if di else ''
        open_tag = open_tag.replace(attr, '') if attr else open_tag
        return open_tag + ICONS[key] + '<span class="bk-tl"' + attr + '>' + mo.group(3) + '</span></button>'
    s, n1 = re.subn(r'(<button type="button" class="tab[^"]*" data-tab="(duty|adv|set)"[^>]*>)([^<]*)</button>', lambda mo: icon(mo), s)
    s, n2 = re.subn(r'(<button id="t-(duty|adv|set)"[^>]*>)([^<]*)</button>', lambda mo: icon(mo), s)
    assert n1 + n2 == 3, (path, n1, n2)
    assert '</head>' in s
    s = s.replace('</head>', '<style>' + CSS + '</style></head>', 1)
    assert '</body>' in s
    s = s.replace('</body>', JS + '</body>', 1)
    open(path, "w", encoding="utf-8").write(s)
    return True

if __name__ == "__main__":
    out = sys.argv[1]
    for page in ("Work", "forall"):
        print(page, "patched" if patch(os.path.join(out, page, "index.html")) else "already patched")

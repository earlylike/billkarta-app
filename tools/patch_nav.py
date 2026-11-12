#!/usr/bin/env python3
"""Turns the top Duty / Advance / Settings tabs into a fixed bottom navigation bar.
Usage: patch_nav.py <work|forall> <index.html>   (edits the file in place; safe to re-run)"""
import sys

MARK = "/* BK-BOTTOM-NAV */"

def icon(paths):
    svg = ("<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='black' "
           "stroke-width='1.9' stroke-linecap='round' stroke-linejoin='round'>" + paths + "</svg>")
    enc = svg.replace("<", "%3C").replace(">", "%3E").replace("#", "%23")
    return 'url("data:image/svg+xml,' + enc + '")'

ICON_DUTY = icon("<rect x='3' y='5' width='18' height='16' rx='3'/><path d='M3 10h18M8 3v4M16 3v4'/><path d='M9 15.2l2 2 4-4.2'/>")
ICON_ADV = icon("<rect x='2.5' y='6' width='19' height='12' rx='2.5'/><circle cx='12' cy='12' r='2.6'/><path d='M6 12h.01M18 12h.01'/>")
ICON_SET = icon("<path d='M4 7h9M17 7h3M4 17h3M11 17h9'/><circle cx='15' cy='7' r='2'/><circle cx='9' cy='17' r='2'/>")

CFG = {
    "work": dict(
        nav="nav.tabs", btn="nav.tabs .tab",
        on="nav.tabs .tab.on",
        duty='nav.tabs .tab[data-tab="duty"]', adv='nav.tabs .tab[data-tab="adv"]', set='nav.tabs .tab[data-tab="set"]',
    ),
    "forall": dict(
        nav='nav[role="tablist"]', btn='nav[role="tablist"] button',
        on='nav[role="tablist"] button[aria-selected="true"]',
        duty="#t-duty", adv="#t-adv", set="#t-set",
    ),
}

def build_css(c):
    return f"""
{MARK}
{c['nav']}{{position:fixed;left:0;right:0;bottom:0;top:auto;margin:0;max-width:none;display:flex;gap:0;
  background:var(--card,#fff);border-top:1px solid var(--line,rgba(0,0,0,.08));
  box-shadow:0 -6px 22px rgba(16,24,40,.12);padding:.3rem .4rem calc(.3rem + env(safe-area-inset-bottom,0px));
  z-index:60;-webkit-tap-highlight-color:transparent}}
{c['btn']}{{position:relative;flex:1;min-height:3.6rem;display:flex;flex-direction:column;align-items:center;
  justify-content:flex-end;gap:.2rem;padding:.25rem 0 .3rem;margin:0;border:0;border-radius:14px;
  background:transparent;box-shadow:none;color:var(--muted,var(--ink));opacity:1;font:inherit;
  font-size:.72rem;font-weight:500;line-height:1.1;cursor:pointer;transition:color .15s,opacity .15s}}
{c['btn']}::before{{content:"";width:3.4rem;height:1.9rem;border-radius:999px;background:transparent;transition:background .2s}}
{c['btn']}::after{{content:"";position:absolute;left:50%;top:.55rem;width:1.35rem;height:1.35rem;
  transform:translateX(-50%);background:currentColor;
  -webkit-mask:var(--bk-ic) center/contain no-repeat;mask:var(--bk-ic) center/contain no-repeat}}
{c['on']}{{background:transparent;color:var(--accent);opacity:1;font-weight:700;box-shadow:none;border:0}}
{c['on']}::before{{background:rgba(99,102,241,.16);background:color-mix(in srgb,var(--accent) 16%,transparent)}}
{c['duty']}{{--bk-ic:{ICON_DUTY}}}
{c['adv']}{{--bk-ic:{ICON_ADV}}}
{c['set']}{{--bk-ic:{ICON_SET}}}
{c['btn']}:focus-visible{{outline:2px solid var(--accent);outline-offset:-2px}}
body::after{{content:"";display:block;height:calc(5.2rem + env(safe-area-inset-bottom,0px))}}
body.bk-kbd {c['nav']}{{display:none}}
body.bk-kbd::after{{height:1rem}}
"""

JS = """<script>
/* BK-BOTTOM-NAV: hide the bar while the on-screen keyboard is open */
(function(){var b=document.body,t;
function on(e){var n=e.target&&e.target.tagName;if(n==='INPUT'||n==='TEXTAREA'||n==='SELECT'){clearTimeout(t);b.classList.add('bk-kbd');}}
function off(){t=setTimeout(function(){b.classList.remove('bk-kbd');},150);}
document.addEventListener('focusin',on);document.addEventListener('focusout',off);})();
</script>
"""

def main():
    kind, path = sys.argv[1], sys.argv[2]
    s = open(path, encoding="utf-8").read()
    if MARK in s:
        print("already patched:", path); return
    i = s.rfind("</style>")
    j = s.rfind("</body>")
    if i < 0 or j < 0:
        sys.exit("could not find </style> or </body> in " + path)
    s = s[:i] + build_css(CFG[kind]) + s[i:]
    j = s.rfind("</body>")
    s = s[:j] + JS + s[j:]
    open(path, "w", encoding="utf-8").write(s)
    print("patched:", path)

main()

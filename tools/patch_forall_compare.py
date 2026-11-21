#!/usr/bin/env python3
"""App-only: adds a "Compare PDF" card under "Make A Bill" on the Duty Manager page.
Pick an employee, choose a PDF, compare its duties/advances with the saved records, get a marked, corrected PDF.
Usage: patch_forall_compare.py <assets/www folder>   (idempotent; run by sync-pages.sh after patch_forall_pdf_style.py)"""
import os, sys
MARK = "BK-COMPARE-PDF"
here = os.path.dirname(os.path.abspath(__file__))
p = os.path.join(sys.argv[1], "forall", "index.html")
s = open(p, encoding="utf-8").read()
if MARK in s:
    print("compare PDF already patched"); sys.exit(0)

CARD = '''
    <div class="card" id="cmp"><!-- BK-COMPARE-PDF -->
      <h2 class="savedh"><span data-i18n="cmp_title">Compare PDF</span></h2>
      <label for="cname" style="margin-top:0" data-i18n="bill_search">Enter Employee Name</label>
      <div class="ac">
        <input type="text" id="cname" data-i18n-ph="bname_ph" placeholder="Type employee name" autocomplete="off" role="combobox" aria-expanded="false" aria-controls="clist" aria-autocomplete="list">
        <ul id="clist" class="aclist" role="listbox" hidden></ul>
      </div>
      <div id="cstep" hidden>
        <input type="file" id="cfile" accept="application/pdf,.pdf" hidden>
        <button class="btn save" id="cpick" type="button" data-i18n="cmp_choose">Choose PDF from phone</button>
        <p class="hint" id="cnote" style="font-size:.78rem;margin:.45rem 0 0"></p>
        <p class="hint" id="cfname"></p>
        <div class="brow" style="margin-top:.8rem;align-items:center"><span class="bl"><label for="cpend" data-i18n="pending" style="margin:0">Pending payment</label><small style="display:block;opacity:.7" data-i18n="cmp_hint">Optional, added to the bill</small></span><span class="bv"><input type="number" id="cpend" class="pendin" min="0" step="any" inputmode="decimal" placeholder="0"></span></div>
        <button class="btn save" id="cgo" type="button" data-i18n="cmp_title">Compare PDF</button>
      </div>
      <p class="msg" id="cmsg" aria-live="polite"></p>
    </div>
'''
SHEET = '''
<div id="cmpsheet" hidden><div class="cmpbox" role="dialog" aria-modal="true" aria-labelledby="cmptitle">
  <div class="cmphd"><b id="cmptitle"></b><button type="button" id="cmpx" data-i18n-aria="cmp_close" aria-label="Close">&#10005;</button></div>
  <div id="cmpbody"><div id="cmplist"></div></div>
  <button class="btn save" id="cmpdl" type="button" data-i18n="cmp_dl">Download PDF</button>
</div></div>
<style>
#bill.card,#cmp.card{--tint:#fdf1c2}
#cmp{scroll-margin-top:96px}
#cmpsheet{position:fixed;inset:0;z-index:200;background:rgba(0,0,0,.6);display:flex;align-items:flex-end;justify-content:center}
#cmpsheet[hidden]{display:none}
.cmpbox{width:100%;max-width:560px;height:92vh;display:flex;flex-direction:column;background:#e9ebef;color:#17233b;border-radius:16px 16px 0 0;padding:0 0 10px;box-sizing:border-box}
.cmphd{display:flex;justify-content:space-between;align-items:center;gap:10px;font-size:1.05rem;padding:12px 14px 6px}
.cmphd button{background:none;border:none;color:#17233b;font-size:20px;padding:4px 8px;cursor:pointer}
#cmpbody{flex:1;overflow:auto;padding:4px 8px 8px}
.cmpbox>.btn{margin:4px 10px 0;width:auto}
.cmppg{background:#fff;font-family:Arial,Helvetica,sans-serif;font-size:11px;color:#282828;box-shadow:0 0 0 1px #d5d9de}
.cmpban{background:#4338ca;color:#fff;text-align:center;font-weight:700;font-size:16px;padding:16px 8px;overflow-wrap:anywhere}
.cmpwrap{padding:12px 4px 14px 10px}
.cmpr{display:grid;position:relative}
.cmpr.d{grid-template-columns:minmax(0,22%) minmax(0,1fr) 13% 13% 26px}
.cmpr.a{grid-template-columns:minmax(0,1fr) minmax(0,1fr) 26px}
.cmpr>div:not(.cmm){border:.5px solid #c8cdd2;padding:6px 5px;display:flex;align-items:center;background:#fff;overflow-wrap:anywhere}
.cmpr>div.hd{background:#1e8259;color:#fff;font-weight:700;border-color:#1e8259;justify-content:center}
.cmpr>.hl{justify-content:flex-start}
.cmpr>.c{justify-content:center}
.cmpr>.am{justify-content:flex-end}
.cmpr>.cmm{display:flex;align-items:center;justify-content:center}
.cmpr.bad::after{content:"";position:absolute;left:0;right:26px;top:50%;border-top:2px solid #d93025;pointer-events:none}
.cmpr.fix>div:not(.cmm){background:#eaf3de;border-color:#97c459}
.cmpr.tot>div:not(.cmm){background:#e7ecf3;font-weight:700}
.cmpr.tot.fix>div:not(.cmm){background:#eaf3de}
.cmk{width:15px;height:15px;border-radius:4px;color:#fff;font-size:11px;display:inline-flex;align-items:center;justify-content:center;flex:none}
.cmk.g{background:#1e8259}.cmk.x{background:#d93025}
.cmph{margin:14px 0 6px;font-size:13px;color:#1e8259;font-weight:700}
.cmpbill{border:1.5px solid #0f766e;border-radius:10px;padding:10px 12px;font-size:12.5px;color:#17233b}
.cmpl{display:flex;align-items:center;gap:6px;margin:0 0 7px;line-height:1.3}
.cmpl.bad span:first-child{color:#d93025;text-decoration:line-through;font-size:11.5px}
.cmpfinal{font-weight:700;color:#0f766e;font-size:15px}
</style>
'''
a = s.index('    <div class="card" id="details">')
s = s[:a] + CARD.lstrip("\n") + SHEET + "\n" + s[a:]
js = open(os.path.join(here, "forall_compare.js"), encoding="utf-8").read()
c = s.index("  function makeDetailsPdf() {")
s = s[:c] + js + "\n" + s[c:]
import json
TR = json.load(open(os.path.join(here, "forall_compare_i18n.json"), encoding="utf-8"))
for lg, d in TR.items():
    items = ", ".join(json.dumps(k, ensure_ascii=False) + ": " + json.dumps(v, ensure_ascii=False) for k, v in d.items())
    key = lg + ': {"complete_bill"'
    assert s.count(key) == 1, lg
    s = s.replace(key, lg + ': {' + items + ', "complete_bill"', 1)
open(p, "w", encoding="utf-8").write(s)
print("compare PDF patched")

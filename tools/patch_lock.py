#!/usr/bin/env python3
"""Duty Manager + Senior Manager. Run AFTER patch_headadv.py.
 - Rates card renamed "Payment Per Duty" / "Save payment" (8 languages), medium heading font
 - Saved duties table: lock icon below the date. Entries are locked; edit/delete on a locked entry only shows a message
   until the lock is tapped. The entry locks again when the edit dialog closes.
 - Senior Manager only: Half/Full cannot be changed when editing (saved duty is shown, other option dimmed)."""
import json, os, re, sys
root = sys.argv[1]
LG = ["en", "hi", "mr", "gu", "pa", "ta", "te", "kn"]
RATES = {"en": ["Payment for Employee per day", "Save payment"], "hi": ["कर्मचारी का प्रतिदिन भुगतान", "भुगतान सेव करें"], "mr": ["कर्मचाऱ्याचे प्रतिदिन पेमेंट", "पेमेंट सेव्ह करा"],
  "gu": ["કર્મચારીની પ્રતિ દિવસ ચુકવણી", "ચુકવણી સાચવો"], "pa": ["ਕਰਮਚਾਰੀ ਦਾ ਪ੍ਰਤੀ ਦਿਨ ਭੁਗਤਾਨ", "ਭੁਗਤਾਨ ਸੰਭਾਲੋ"], "ta": ["ஊழியருக்கு ஒரு நாள் கட்டணம்", "கட்டணத்தைச் சேமி"],
  "te": ["ఉద్యోగికి రోజుకు చెల్లింపు", "చెల్లింపు సేవ్ చేయండి"], "kn": ["ನೌಕರರಿಗೆ ದಿನಕ್ಕೆ ಪಾವತಿ", "ಪಾವತಿ ಉಳಿಸಿ"]}
LK = {"en": ["Tap the lock icon to unlock this entry", "Unlock this entry", "Lock this entry"],
  "hi": ["इस एंट्री को खोलने के लिए लॉक आइकन पर टैप करें", "एंट्री अनलॉक करें", "एंट्री लॉक करें"],
  "mr": ["ही नोंद अनलॉक करण्यासाठी लॉक आयकॉनवर टॅप करा", "नोंद अनलॉक करा", "नोंद लॉक करा"],
  "gu": ["આ એન્ટ્રી અનલૉક કરવા લૉક આઇકન પર ટેપ કરો", "એન્ટ્રી અનલૉક કરો", "એન્ટ્રી લૉક કરો"],
  "pa": ["ਇਹ ਐਂਟਰੀ ਅਨਲੌਕ ਕਰਨ ਲਈ ਲੌਕ ਆਈਕਨ ’ਤੇ ਟੈਪ ਕਰੋ", "ਐਂਟਰੀ ਅਨਲੌਕ ਕਰੋ", "ਐਂਟਰੀ ਲੌਕ ਕਰੋ"],
  "ta": ["இந்த பதிவைத் திறக்க பூட்டு ஐகானைத் தட்டவும்", "பதிவைத் திற", "பதிவைப் பூட்டு"],
  "te": ["ఈ ఎంట్రీని అన్‌లాక్ చేయడానికి లాక్ ఐకాన్‌ను నొక్కండి", "ఎంట్రీ అన్‌లాక్ చేయండి", "ఎంట్రీ లాక్ చేయండి"],
  "kn": ["ಈ ಎಂಟ್ರಿಯನ್ನು ಅನ್‌ಲಾಕ್ ಮಾಡಲು ಲಾಕ್ ಐಕಾನ್ ಟ್ಯಾಪ್ ಮಾಡಿ", "ಎಂಟ್ರಿ ಅನ್‌ಲಾಕ್ ಮಾಡಿ", "ಎಂಟ್ರಿ ಲಾಕ್ ಮಾಡಿ"]}

CSS = """<style>/* BK-LOCK */.lkb{display:grid;place-items:center;width:28px;height:28px;margin-top:6px;padding:0;border:0;border-radius:50%;background:#b45309;color:#fff;cursor:pointer}.lkb.open{background:#16a34a}.lkb svg{width:16px;height:16px;fill:none;stroke:currentColor;stroke-width:2.6;stroke-linecap:round;stroke-linejoin:round}tr.lkd .acts .ibtn{opacity:.4}#lktoast{position:fixed;left:50%;bottom:86px;transform:translateX(-50%);z-index:9999;max-width:88vw;background:#111827;color:#fff;padding:.6rem 1rem;border-radius:999px;font-size:.85rem;font-weight:600;text-align:center;box-shadow:0 6px 16px rgba(0,0,0,.35);opacity:0;pointer-events:none;transition:opacity .2s}#lktoast.on{opacity:1}[data-i18n="rates"].ratesh-t{font-size:.86rem}.seg input:disabled:not(:checked)+span{opacity:.4;cursor:not-allowed}.seg input:disabled+span{cursor:default}</style>"""

JS = r'''
  /* BK-LOCK: saved entries are locked until the lock under the date is tapped */
  var lkOpen = {};
  var LK_LOCK = '<svg viewBox="0 0 24 24" aria-hidden="true"><rect x="5" y="11" width="14" height="9" rx="2"/><path d="M8 11V8a4 4 0 018 0v3"/></svg>';
  var LK_OPEN = '<svg viewBox="0 0 24 24" aria-hidden="true"><rect x="5" y="11" width="14" height="9" rx="2"/><path d="M8 11V8a4 4 0 017.5-2"/></svg>';
  var lkTimer = null;
  function lkToast() {
    var t = document.getElementById("lktoast");
    if (!t) { t = document.createElement("div"); t.id = "lktoast"; t.setAttribute("role", "status"); document.body.appendChild(t); }
    t.textContent = tx("lk_msg"); t.classList.add("on");
    clearTimeout(lkTimer); lkTimer = setTimeout(function () { t.classList.remove("on"); }, 2400);
  }
  function applyLocks() {
    var rows = [].slice.call(document.querySelectorAll("#list tr[data-rid]"));
    rows.forEach(function (tr, i) {
      var id = tr.getAttribute("data-rid");
      var cell = tr.querySelector("td.g") || (tr.querySelector("td.g") === null && !tr.querySelector("td.mnm") ? tr.firstElementChild : null);
      var group = [tr];
      if (cell && cell.rowSpan > 1) { for (var k = 1; k < cell.rowSpan && rows[i + k]; k++) group.push(rows[i + k]); }
      var ids = group.map(function (g) { return g.getAttribute("data-rid"); });
      var open = ids.every(function (x) { return lkOpen[x]; });
      group.forEach(function (g) { g.classList.toggle("lkd", !lkOpen[g.getAttribute("data-rid")]); });
      if (!cell) return;
      var old = cell.querySelector(".lkb"); if (old) old.remove();
      var b = document.createElement("button"); b.type = "button"; b.className = "lkb" + (open ? " open" : "");
      b.setAttribute("data-lk", ids.join(",")); b.innerHTML = open ? LK_OPEN : LK_LOCK;
      var lbl = open ? tx("lk_lock") : tx("lk_unlock"); b.title = lbl; b.setAttribute("aria-label", lbl);
      cell.appendChild(b);
    });
  }
  $("list").addEventListener("click", function (ev) {
    var t = ev.target.closest ? ev.target : null; if (!t) return;
    var lk = t.closest(".lkb");
    if (lk) {
      ev.stopPropagation();
      var ids = lk.getAttribute("data-lk").split(","), open = ids.every(function (x) { return lkOpen[x]; });
      ids.forEach(function (x) { if (open) delete lkOpen[x]; else lkOpen[x] = 1; });
      applyLocks(); return;
    }
    var eb = t.closest("[data-edit]") || t.closest("[data-del]");
    if (eb && !lkOpen[eb.getAttribute("data-edit") || eb.getAttribute("data-del")]) { ev.stopPropagation(); lkToast(); }
  }, true);
'''

for page in ["forall", "mom"]:
    fp = os.path.join(root, page, "index.html")
    f = open(fp, encoding="utf-8").read()
    if "BK-LOCK" in f:
        print("lock: %s already patched" % page); continue
    def rep(a, b, n=1):
        global f
        assert f.count(a) == n, (page, f.count(a), a[:90])
        f = f.replace(a, b)
    rep("</head>", CSS + "</head>") if page == "mom" else rep("</style></head>", "</style>" + CSS + "</head>") if f.count("</style></head>") == 1 else rep("</head>", CSS + "</head>")
    rep("  function renderList() {", "  function renderList() { renderList0(); applyLocks(); }\n  function renderList0() {")
    rep('  $("list").onclick = function (ev) {', JS + '  $("list").onclick = function (ev) {')
    rep('function closeEdit() { $("emodal").hidden = true; editId = null; }', 'function closeEdit() { $("emodal").hidden = true; if (editId) delete lkOpen[editId]; editId = null; applyLocks(); }')
    if page == "mom":
        rep('''document.querySelectorAll('input[name="eduty"]'), function (i) { i.checked = i.value === r.duty; });''', '''document.querySelectorAll('input[name="eduty"]'), function (i) { i.checked = i.value === r.duty; i.disabled = true; });''')
    # translations
    for lg in LG:
        m = re.search(r'(\n?\s*(?:var I18N = \{ )?%s: \{)(")' % lg, f); assert m, lg
        ins = '"lk_msg": %s, "lk_unlock": %s, "lk_lock": %s, ' % tuple(json.dumps(x, ensure_ascii=False) for x in LK[lg])
        f = f[:m.end(1)] + ins + f[m.end(1):]
        line_start = f.index(m.group(1).lstrip("\n")) if False else m.start()
        end = f.index("\n", m.end())
        seg = f[m.start():end]
        seg2 = re.sub(r'"rates": ?"(?:[^"\\]|\\.)*"', '"rates": %s' % json.dumps(RATES[lg][0], ensure_ascii=False), seg, count=1)
        seg2 = re.sub(r'"save_rates": ?"(?:[^"\\]|\\.)*"', '"save_rates": %s' % json.dumps(RATES[lg][1], ensure_ascii=False), seg2, count=1)
        assert seg2 != seg, lg
        f = f[:m.start()] + seg2 + f[end:]
    rep('data-i18n="rates">Rates</span>', 'data-i18n="rates">Payment for Employee per day</span>')
    rep('data-i18n="save_rates">Save rates</button>', 'data-i18n="save_rates">Save payment</button>')
    open(fp, "w", encoding="utf-8").write(f)
    print("lock: %s patched" % page)

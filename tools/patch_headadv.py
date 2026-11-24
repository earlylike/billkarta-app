#!/usr/bin/env python3
"""Duty Manager only. Run AFTER patch_heads.py.
 - Advance tab: card "My Advance from Head Of Manager" (tap a head -> same advance dialog, stored per head in state.hadv)
 - My Total Bill (card + PDF): the chosen head's advances are listed and SUBTRACTED ("Advance has been subtracted.")
 - Backup keeps head advances; deleting/restoring a head keeps its advances (same id)
 - Manager of Managers check: advance + subtracted total are compared. All texts in 8 languages."""
import json, os, re, sys
root = sys.argv[1]
fp = os.path.join(root, "forall", "index.html")
f = open(fp, encoding="utf-8").read()
if "BK-HEADADV" in f:
    print("headadv: already patched"); sys.exit(0)

def rep(a, b, n=1):
    global f
    assert f.count(a) == n, (f.count(a), a[:100])
    f = f.replace(a, b)

# state
rep("trash: [], heads: [] };", "trash: [], heads: [], hadv: [] };")
rep("if (!state.heads) state.heads = [];", "if (!state.heads) state.heads = []; if (!state.hadv) state.hadv = [];")

# new card on the Advance tab
CARD = '''
    <div class="card" id="hadvcard">
      <!-- BK-HEADADV -->
      <h2 class="advh"><span class="advh-ic" aria-hidden="true"><svg viewBox="0 0 24 24"><circle cx="12" cy="8" r="3.8"/><path d="M4.5 20a7.5 7.5 0 0115 0"/></svg></span><span class="advh-t" data-i18n="hadv_title">My Advance from Head Of Manager</span></h2>
      <p class="hint" style="margin:0 0 .8rem" data-i18n="hadv_hint">Tap a head to add an advance.</p>
      <div id="halist"></div>
      <p class="msg" id="hadvmsg" aria-live="polite"></p>
    </div>
'''
rep('''      <div id="alist"></div>
      <p class="msg" id="advmsg" aria-live="polite"></p>
    </div>
''', '''      <div id="alist"></div>
      <p class="msg" id="advmsg" aria-live="polite"></p>
    </div>
''' + CARD)

# advance dialog: works for an employee OR a head
rep('''    advEmpId = emp.id;
    $("at").textContent''', '''    advEmpId = emp.id; advHeadId = null;
    $("at").textContent''')
rep('function closeAdvance() { $("amodal").hidden = true; advEmpId = null; }', 'function closeAdvance() { $("amodal").hidden = true; advEmpId = null; advHeadId = null; }')
rep('''    var list = state.advances.filter(function (x) { return x.empId === advEmpId; })
      .sort(''', '''    var list = (advHeadId ? state.hadv.filter(function (x) { return x.headId === advHeadId; }) : state.advances.filter(function (x) { return x.empId === advEmpId; }))
      .sort(''')
rep('$("atot").textContent = list.length ? tx("total") + " " + money(advTotal(advEmpId)) : "";',
    '$("atot").textContent = list.length ? tx("total") + " " + money(advHeadId ? list.reduce(function (t, x) { return t + x.amount; }, 0) : advTotal(advEmpId)) : "";')
rep('''          state.advances = state.advances.filter(function (x) { return x.id !== a.id; });
          persist(); renderAdvHist(); renderAdv(); renderBill(); renderDetails();''', '''          if (advHeadId) state.hadv = state.hadv.filter(function (x) { return x.id !== a.id; }); else state.advances = state.advances.filter(function (x) { return x.id !== a.id; });
          persist(); renderAdvHist(); renderAdv(); renderHeadAdv(); renderBill(); renderDetails();''')
rep('''  function saveAdvance() {
''', '''  function saveAdvance() {
    if (advHeadId) return saveHeadAdvance();
''')

JS = r'''
  /* BK-HEADADV: advance taken from a Head Of Manager */
  var advHeadId = null;
  function headAdvTotal(id) { return state.hadv.filter(function (x) { return x.headId === id; }).reduce(function (t, x) { return t + x.amount; }, 0); }
  function headObj(name) { return state.heads.filter(function (h) { return h.name === name; })[0]; }
  function curHeadAdv() {
    var h = headObj(curHead); if (!h) return [];
    return state.hadv.filter(function (x) { return x.headId === h.id; }).sort(function (a, b) { return a.date < b.date ? -1 : a.date > b.date ? 1 : 0; });
  }
  function renderHeadAdv() {
    var box = $("halist"); if (!box) return; box.innerHTML = "";
    if (!state.heads.length) { box.innerHTML = '<p class="hint">' + esc(tx("hm_none")) + '</p>'; return; }
    state.heads.forEach(function (h, i) {
      var row = document.createElement("button"); row.type = "button"; row.className = "arow"; row.setAttribute("data-id", h.id);
      row.innerHTML = '<span class="num"></span><span class="avatar" aria-hidden="true"></span><span class="ename"></span><span class="atotal"></span>';
      row.querySelector(".num").textContent = i + 1;
      row.querySelector(".avatar").textContent = (graphemes(h.name)[0] || "?").toUpperCase();
      row.querySelector(".ename").textContent = h.name;
      var t = headAdvTotal(h.id);
      row.querySelector(".atotal").textContent = t > 0 ? tx("advance") + " " + money(t) : "";
      row.onclick = function () { openHeadAdvance(h); };
      box.appendChild(row);
    });
  }
  function openHeadAdvance(h) {
    advHeadId = h.id; advEmpId = null;
    $("at").textContent = tx("hadv_for", { name: h.name });
    $("adate").value = today(); $("aamt").value = ""; say($("amsg"), "", true);
    renderAdvHist();
    $("amodal").hidden = false; $("aamt").focus();
  }
  function saveHeadAdvance() {
    var h = state.heads.filter(function (x) { return x.id === advHeadId; })[0];
    if (!h) return closeAdvance();
    var date = $("adate").value, amt = Math.round(parseFloat($("aamt").value) * 100) / 100;
    if (!date) return say($("amsg"), tx("choose_date"), true);
    if (!(amt > 0)) return say($("amsg"), tx("enter_amount"), true);
    state.hadv.push({ id: uid(), headId: h.id, date: date, amount: amt });
    persist(); closeAdvance(); renderHeadAdv(); renderDetails();
    say($("hadvmsg"), tx("hadv_saved", { amt: money(amt), name: h.name }));
    flashRow("halist", h.id);
  }
'''
rep("  function refreshAll() {", JS + "  function refreshAll() {")
# renderHeads also refreshes the advance list (names / add / delete / restore)
rep("    syncHeadPickers();\n  }\n  function headDup", "    syncHeadPickers(); if (typeof renderHeadAdv === \"function\") renderHeadAdv();\n  }\n  function headDup")

# trash / restore keeps the head's id so its advances stay attached
rep('state.trash.push({ id: uid(), kind: "head", name: h.name,', 'state.trash.push({ id: uid(), kind: "head", headId: h.id, name: h.name,')
rep('state.heads.push({ id: uid(), name: t.name });\n    state.trash', 'state.heads.push({ id: t.headId || uid(), name: t.name });\n    state.trash')
rep('if (t.kind === "head") nt.kind = "head";', 'if (t.kind === "head") { nt.kind = "head"; if (t.headId !== undefined && t.headId !== null) nt.headId = t.headId; }')

# backup
rep("rates: state.rates, heads: state.heads }", "rates: state.rates, heads: state.heads, hadv: state.hadv }")
rep("pending: {}, heads: [] };\n", "pending: {}, heads: [], hadv: [] };\n    (Array.isArray(d.hadv) ? d.hadv : []).forEach(function (a) { if (a && a.headId !== undefined && a.headId !== null && typeof a.date === \"string\" && Number(a.amount) > 0) out.hadv.push({ id: a.id !== undefined && a.id !== null ? a.id : uid(), headId: a.headId, date: a.date, amount: Number(a.amount) }); });\n")

# My Total Bill card
rep('''      '<div class="dcomplete"><div class="dc-row"><span>' + esc(tx("complete_bill")) + '</span><b>' + esc(moneyS(complete)) + '</b></div></div>' +''',
    '''      (function () {
        var ha = curHeadAdv().reduce(function (t, x) { return t + x.amount; }, 0);
        if (!(ha > 0)) return '<div class="dcomplete"><div class="dc-row"><span>' + esc(tx("complete_bill")) + '</span><b>' + esc(moneyS(complete)) + '</b></div></div>';
        return '<div class="dcomplete"><div class="dc-row dc-sub"><span>' + esc(PS("Total Payment")) + '</span><b>' + esc(moneyS(complete)) + '</b></div>' +
          '<div class="dc-row dc-sub"><span>' + esc(tx("advance")) + '</span><b>- ' + esc(money(ha)) + '</b></div>' +
          '<div class="dc-row dc-fin"><span>' + esc(tx("complete_bill")) + '</span><b>' + esc(moneyS(complete - ha)) + '</b></div>' +
          '<p class="dc-note">' + esc(PS("Advance has been subtracted.")) + '</p></div>';
      })() +''')
rep("  .dcomplete .dc-note{", "  .dc-sub span{font-weight:600;font-size:.95rem}.dc-sub b{font-size:1.05rem;color:#fff}.dc-fin{margin-top:.45rem;padding-top:.45rem;border-top:1px solid rgba(255,255,255,.3)}\n  .dcomplete .dc-note{")

# My Total Bill PDF: head advances only, subtracted
rep('''    var hk = Object.keys(hr), fk = Object.keys(fr), ids = {}, advRows = [], adv = 0;
    state.employees.forEach(function (e) { ids[e.id] = 1; });
    state.advances.forEach(function (a) { if (ids[a.empId]) { advRows.push({ date: a.date, amount: a.amount }); adv += a.amount; } });
    advRows.sort(function (p, q) { return p.date < q.date ? -1 : p.date > q.date ? 1 : 0; });''',
    '''    var hk = Object.keys(hr), fk = Object.keys(fr), advRows = [], adv = 0;
    curHeadAdv().forEach(function (a) { advRows.push({ date: a.date, amount: a.amount }); adv += a.amount; });''')
rep("adv: adv, net: hAmt + fAmt, pend: 0, advRows: advRows };", "adv: adv, net: hAmt + fAmt - adv, pend: 0, advRows: advRows };")
rep('doc.roundedRect(14, y, W - 28, my ? 48 : 78, 3, 3, "S");', 'doc.roundedRect(14, y, W - 28, my ? (b.adv > 0 ? 77 : 48) : 78, 3, 3, "S");')
rep('    if (!my) line(PS("Advance") + ": - " + money(b.adv), 20, y + 38, 12, false, ink);', '    if (!my || b.adv > 0) line(PS("Advance") + ": - " + money(b.adv), 20, y + 38, 12, false, ink);')
rep('    if (!my) line(money(gross) + " - " + money(b.adv) + " = " + money(net1), 20, y + 47, 12, false, ink);', '    if (!my || b.adv > 0) line(money(gross) + " - " + money(b.adv) + " = " + money(net1), 20, y + 47, 12, false, ink);')
rep('line(PS("Final Payment") + " = " + money(b.net), 20, y + (my ? 40 : 68), 16, true, teal);',
    'line(PS("Final Payment") + " = " + money(b.net), 20, y + (my ? (b.adv > 0 ? 58 : 40) : 68), 16, true, teal);\n    if (my && b.adv > 0) line(PS("Advance has been subtracted."), 20, y + 69, 10, false, [90, 100, 120]);')

# translations
G = {
 "en": ["My Advance from Head Of Manager", "Tap a head to add an advance.", "Advance from {name}", "Advance of {amt} saved from {name}.", "Advance has been subtracted."],
 "hi": ["हेड ऑफ मैनेजर से मेरा एडवांस", "एडवांस जोड़ने के लिए हेड पर टैप करें।", "{name} से एडवांस", "{name} से {amt} का एडवांस सेव हो गया।"],
 "mr": ["हेड ऑफ मॅनेजरकडून माझी उचल", "उचल नोंदवण्यासाठी हेडवर टॅप करा.", "{name} यांच्याकडून उचल", "{name} यांच्याकडून {amt} उचल जतन झाली."],
 "gu": ["હેડ ઓફ મેનેજર પાસેથી મારો એડવાન્સ", "એડવાન્સ ઉમેરવા હેડ પર ટેપ કરો.", "{name} પાસેથી એડવાન્સ", "{name} પાસેથી {amt} નો એડવાન્સ સાચવ્યો."],
 "pa": ["ਹੈੱਡ ਆਫ ਮੈਨੇਜਰ ਤੋਂ ਮੇਰਾ ਐਡਵਾਂਸ", "ਐਡਵਾਂਸ ਜੋੜਨ ਲਈ ਹੈੱਡ ’ਤੇ ਟੈਪ ਕਰੋ।", "{name} ਤੋਂ ਐਡਵਾਂਸ", "{name} ਤੋਂ {amt} ਦਾ ਐਡਵਾਂਸ ਸੰਭਾਲਿਆ ਗਿਆ।"],
 "ta": ["ஹெட் ஆஃப் மேனேஜரிடமிருந்து என் முன்பணம்", "முன்பணம் சேர்க்க ஒரு ஹெட்டைத் தட்டவும்.", "{name} இடமிருந்து முன்பணம்", "{name} இடமிருந்து {amt} முன்பணம் சேமிக்கப்பட்டது."],
 "te": ["హెడ్ ఆఫ్ మేనేజర్ నుండి నా అడ్వాన్స్", "అడ్వాన్స్ జోడించడానికి హెడ్ మీద నొక్కండి.", "{name} నుండి అడ్వాన్స్", "{name} నుండి {amt} అడ్వాన్స్ సేవ్ అయింది."],
 "kn": ["ಹೆಡ್ ಆಫ್ ಮ್ಯಾನೇಜರ್ ಅವರಿಂದ ನನ್ನ ಅಡ್ವಾನ್ಸ್", "ಅಡ್ವಾನ್ಸ್ ಸೇರಿಸಲು ಹೆಡ್ ಅನ್ನು ಟ್ಯಾಪ್ ಮಾಡಿ.", "{name} ಅವರಿಂದ ಅಡ್ವಾನ್ಸ್", "{name} ಅವರಿಂದ {amt} ಅಡ್ವಾನ್ಸ್ ಉಳಿಸಲಾಗಿದೆ."]}
KEYS = ["hadv_title", "hadv_hint", "hadv_for", "hadv_saved"]
note = {}
for lg, vals in G.items():
    m = re.search(r'(\n?\s*(?:var I18N = \{ )?%s: \{)(")' % lg, f)
    assert m, lg
    ins = "".join('%s: %s, ' % (json.dumps(k), json.dumps(v, ensure_ascii=False)) for k, v in zip(KEYS, vals))
    f = f[:m.end(1)] + ins + f[m.end(1):]
    if lg != "en":
        i = f.index("%s: {" % lg) if False else None
for lg in ["hi", "mr", "gu", "pa", "ta", "te", "kn"]:
    mm = re.search(r'\n\s*%s: \{.*?"adv_subtracted": ?"\(?([^")]*?)\)?"' % lg, f, re.S)
    note[lg] = mm.group(1)
rep("var PDF_S = {", "var PDF_S = {" + json.dumps("Advance has been subtracted.") + ": " + json.dumps(note, ensure_ascii=False) + ", ")
open(fp, "w", encoding="utf-8").write(f)
print("headadv: patched")

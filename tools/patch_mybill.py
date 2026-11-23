#!/usr/bin/env python3
"""App-only, Duty Manager: "All employees details" becomes "My Bill".
The PDF now uses the Make a Bill layout (title "Manager - <name>", duty table, advance table, bill box without pending payment)
and is saved as "Manager - <name>.pdf". The manager name is typed once in Settings (stored on the phone).
Must run AFTER patch_mom.py (Manager of Managers keeps its own wording).
Usage: patch_mybill.py <assets/www folder>"""
import os, re, sys
path = os.path.join(sys.argv[1], "forall", "index.html")
s = open(path, encoding="utf-8").read()
if "BK-MYBILL" in s:
    print("mybill: already patched"); sys.exit(0)

def rep(a, b, n=1):
    global s
    c = s.count(a)
    assert c == n, (c, n, a[:90])
    s = s.replace(a, b)

# titles + button text in every language
T = {"en": ("My Bill", "Download My Bill"), "hi": ("मेरा बिल", "मेरा बिल डाउनलोड करें"), "mr": ("माझे बिल", "माझे बिल डाउनलोड करा"),
     "gu": ("મારું બિલ", "મારું બિલ ડાઉનલોડ કરો"), "pa": ("ਮੇਰਾ ਬਿੱਲ", "ਮੇਰਾ ਬਿੱਲ ਡਾਊਨਲੋਡ ਕਰੋ"), "ta": ("என் பில்", "என் பில்லை பதிவிறக்கு"),
     "te": ("నా బిల్", "నా బిల్ డౌన్‌లోడ్"), "kn": ("ನನ್ನ ಬಿಲ್", "ನನ್ನ ಬಿಲ್ ಡೌನ್‌ಲೋಡ್")}
for lg, (t, d) in T.items():
    m = re.search(r'(\n?\s*(?:var I18N = \{ )?%s: \{)("cmp_title")' % lg, s)
    assert m, lg
    s = s[:m.end(1)] + '"dl_mybill": "%s", ' % d + s[m.end(1):]
    seg_start = m.start()
    m2 = re.compile(r'"emp_details":\s*"').search(s, seg_start)
    q1 = m2.end(); q2 = s.index('"', q1)
    s = s[:q1] + t + s[q2:]
rep('esc(tx("dl_pdf")) + \'</button><p class="msg" id="dmsg"', 'esc(tx("dl_mybill")) + \'</button><p class="msg" id="dmsg"')

# Make a Bill PDF made reusable
rep('  function makePdf() {\n    var b = billData, msg = $("pmsg");\n    if (!b) return;',
    '  function makePdf() { return makePdfFrom(billData, $("pmsg"), null); }\n  function makePdfFrom(b, msg, my) { /* BK-MYBILL */\n    if (!b) return;')
rep('var nameText = PS("Name") + ": " + (b.name || "____________________");', 'var nameText = my ? my.title : PS("Name") + ": " + (b.name || "____________________");')
rep('r.duty === "Half" ? "1" : "", r.duty === "Full" ? "1" : ""]; }),',
    'b.my ? (r.Half ? String(r.Half) : "") : (r.duty === "Half" ? "1" : ""), b.my ? (r.Full ? String(r.Full) : "") : (r.duty === "Full" ? "1" : "")]; }),')
rep('doc.roundedRect(14, y, W - 28, 78, 3, 3, "S");', 'doc.roundedRect(14, y, W - 28, my ? 66 : 78, 3, 3, "S");')
rep('PS("Half Days") + ": " + b.hd + "  (" + b.hd + " x " + money(b.rh) + " = " + money(b.hAmt) + ")"',
    'PS("Half Days") + ": " + b.hd + (b.rh === null ? "  (" + money(b.hAmt) + ")" : "  (" + b.hd + " x " + money(b.rh) + " = " + money(b.hAmt) + ")")')
rep('PS("Full Days") + ": " + b.fd + "  (" + b.fd + " x " + money(b.rf) + " = " + money(b.fAmt) + ")"',
    'PS("Full Days") + ": " + b.fd + (b.rf === null ? "  (" + money(b.fAmt) + ")" : "  (" + b.fd + " x " + money(b.rf) + " = " + money(b.fAmt) + ")")')
rep('    line(money(net1) + " + " + money(b.pend || 0) + " (" + PS("Pending payment") + ")", 20, y + 58, 12, false, ink);',
    '    if (!my) line(money(net1) + " + " + money(b.pend || 0) + " (" + PS("Pending payment") + ")", 20, y + 58, 12, false, ink);')
rep('line(PS("Final Payment") + " = " + money(b.net), 20, y + 68, 16, true, teal);', 'line(PS("Final Payment") + " = " + money(b.net), 20, y + (my ? 58 : 68), 16, true, teal);')
rep('''    var fname = (b.name.replace(/[^A-Za-z0-9]+/g, "-").replace(/^-|-$/g, "") || "Duty-Log") + "-bill.pdf";
    showPdfActions(fname, buf);''', '''    var fname = my ? my.fname : (b.name.replace(/[^A-Za-z0-9]+/g, "-").replace(/^-|-$/g, "") || "Duty-Log") + "-bill.pdf";
    showPdfActions(fname, buf, my ? my.box : undefined);''')

# My Bill: build the bill data and use the Make a Bill layout
i = s.index("  function makeDetailsPdf() {"); j = s.index("  var pdfUrl = null;", i)
s = s[:i] + '''  function myName() { try { return (localStorage.getItem("dutylog.mname") || "").trim(); } catch (e) { return ""; } }
  function makeDetailsPdf() {
    var d = detData; if (!d) return;
    var hAmt = 0, fAmt = 0, hr = {}, fr = {};
    state.records.forEach(function (r) {
      r.names.forEach(function (n) {
        var e = state.employees.filter(function (x) { return x.name === n; })[0], rt = rateOf(e, r.duty);
        if (r.duty === "Full") { fAmt += rt; fr[rt] = 1; } else { hAmt += rt; hr[rt] = 1; }
      });
    });
    var hk = Object.keys(hr), fk = Object.keys(fr), ids = {}, advRows = [], adv = 0;
    state.employees.forEach(function (e) { ids[e.id] = 1; });
    state.advances.forEach(function (a) { if (ids[a.empId]) { advRows.push({ date: a.date, amount: a.amount }); adv += a.amount; } });
    advRows.sort(function (p, q) { return p.date < q.date ? -1 : p.date > q.date ? 1 : 0; });
    var nm = myName(), title = "Manager" + (nm ? " - " + nm : "");
    var b = { my: true, name: nm, rows: d.rows, hd: d.hd, fd: d.fd, hAmt: hAmt, fAmt: fAmt,
      rh: hk.length === 1 ? Number(hk[0]) : hk.length === 0 ? (Number(state.rates.Half) || 0) : null,
      rf: fk.length === 1 ? Number(fk[0]) : fk.length === 0 ? (Number(state.rates.Full) || 0) : null,
      adv: adv, net: hAmt + fAmt - adv, pend: 0, advRows: advRows };
    makePdfFrom(b, $("dmsg"), { title: title, fname: title.replace(/[\\\\\\/:*?"<>|]+/g, "").trim() + ".pdf", box: "dacts" });
  }
''' + s[j:]

# Settings: manager name, typed once
card = '''<section id="p-set" hidden>
    <div class="card" id="mncard">
      <h2 class="ratesh"><span class="ratesh-t">Manager Name</span></h2>
      <label for="mname" style="margin-top:0">Your name (shown on My Bill PDF)</label>
      <input type="text" id="mname" maxlength="40" autocomplete="off" placeholder="Enter manager name">
      <button class="btn save" id="mnsave" type="button">Save name</button>
      <p class="msg" id="mnmsg" aria-live="polite"></p>
    </div>
'''
rep('<section id="p-set" hidden>\n', card)
rep('  function myName() {', '''  (function () {
    var inp = $("mname"); if (!inp) return;
    try { inp.value = localStorage.getItem("dutylog.mname") || ""; } catch (e) {}
    $("mnsave").onclick = function () {
      var v = inp.value.trim(); inp.value = v;
      try { localStorage.setItem("dutylog.mname", v); say($("mnmsg"), v ? "Saved." : "Name cleared."); } catch (e) { say($("mnmsg"), "Could not save on this phone.", true); }
    };
  })();
  function myName() {''')
open(path, "w", encoding="utf-8").write(s)
print("mybill: patched")

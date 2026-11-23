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
T = {
     "en": ('My Total Bill', 'Download My Total Bill', "Make Employee's Bill", 'Check Employee Bill'),
     "hi": ('मेरा कुल बिल', 'मेरा कुल बिल डाउनलोड करें', 'कर्मचारी का बिल बनाएं', 'कर्मचारी का बिल जांचें'),
     "mr": ('माझे एकूण बिल', 'माझे एकूण बिल डाउनलोड करा', 'कर्मचारीचे बिल तयार करा', 'कर्मचारीचे बिल तपासा'),
     "gu": ('મારું કુલ બિલ', 'મારું કુલ બિલ ડાઉનલોડ કરો', 'કર્મચારીનું બિલ બનાવો', 'કર્મચારીનું બિલ તપાસો'),
     "pa": ('ਮੇਰਾ ਕੁੱਲ ਬਿੱਲ', 'ਮੇਰਾ ਕੁੱਲ ਬਿੱਲ ਡਾਊਨਲੋਡ ਕਰੋ', 'ਕਰਮਚਾਰੀ ਦਾ ਬਿੱਲ ਬਣਾਓ', 'ਕਰਮਚਾਰੀ ਦਾ ਬਿੱਲ ਚੈੱਕ ਕਰੋ'),
     "ta": ('என் மொத்த பில்', 'என் மொத்த பில்லை பதிவிறக்கு', 'ஊழியர் பில் உருவாக்கு', 'ஊழியர் பில் சரிபார்'),
     "te": ('నా మొత్తం బిల్', 'నా మొత్తం బిల్ డౌన్\u200cలోడ్', 'ఉద్యోగి బిల్లు తయారు చేయండి', 'ఉద్యోగి బిల్లు తనిఖీ'),
     "kn": ('ನನ್ನ ಒಟ್ಟು ಬಿಲ್', 'ನನ್ನ ಒಟ್ಟು ಬಿಲ್ ಡೌನ್\u200cಲೋಡ್', 'ಉದ್ಯೋಗಿಯ ಬಿಲ್ ಮಾಡಿ', 'ಉದ್ಯೋಗಿಯ ಬಿಲ್ ಪರಿಶೀಲಿಸಿ'),
}
MN = {'en': ('Manager Name', 'Your name (shown on My Total Bill PDF)', 'Enter manager name', 'Save name'), 'hi': ('मैनेजर का नाम', 'आपका नाम (मेरा कुल बिल PDF पर दिखेगा)', 'मैनेजर का नाम दर्ज करें', 'नाम सेव करें'), 'mr': ('मॅनेजरचे नाव', 'तुमचे नाव (माझे एकूण बिल PDF वर दिसेल)', 'मॅनेजरचे नाव लिहा', 'नाव सेव्ह करा'), 'gu': ('મેનેજરનું નામ', 'તમારું નામ (મારું કુલ બિલ PDF પર દેખાશે)', 'મેનેજરનું નામ લખો', 'નામ સેવ કરો'), 'pa': ('ਮੈਨੇਜਰ ਦਾ ਨਾਮ', 'ਤੁਹਾਡਾ ਨਾਮ (ਮੇਰਾ ਕੁੱਲ ਬਿੱਲ PDF ਤੇ ਦਿਸੇਗਾ)', 'ਮੈਨੇਜਰ ਦਾ ਨਾਮ ਲਿਖੋ', 'ਨਾਮ ਸੇਵ ਕਰੋ'), 'ta': ('மேனேஜர் பெயர்', 'உங்கள் பெயர் (என் மொத்த பில் PDF-ல் தோன்றும்)', 'மேனேஜர் பெயரை உள்ளிடவும்', 'பெயரைச் சேமி'), 'te': ('మేనేజర్ పేరు', 'మీ పేరు (నా మొత్తం బిల్ PDF లో కనిపిస్తుంది)', 'మేనేజర్ పేరు నమోదు చేయండి', 'పేరు సేవ్ చేయండి'), 'kn': ('ಮ್ಯಾನೇಜರ್ ಹೆಸರು', 'ನಿಮ್ಮ ಹೆಸರು (ನನ್ನ ಒಟ್ಟು ಬಿಲ್ PDF ನಲ್ಲಿ ಕಾಣಿಸುತ್ತದೆ)', 'ಮ್ಯಾನೇಜರ್ ಹೆಸರು ನಮೂದಿಸಿ', 'ಹೆಸರು ಉಳಿಸಿ')}
def setkey(s, key, val, lo, hi):
    m = re.compile(r'"%s":\s*"' % key).search(s, lo, hi)
    assert m, (key, lo)
    q1 = m.end(); q2 = s.index('"', q1)
    return s[:q1] + val + s[q2:]
for lg, (t, d, mk, ck) in T.items():
    m = re.search(r'(\n?\s*(?:var I18N = \{ )?%s: \{)("cmp_title")' % lg, s)
    assert m, lg
    s = s[:m.end(1)] + '"dl_mybill": "%s", "mn_title": "%s", "mn_label": "%s", "mn_ph": "%s", "mn_save": "%s", ' % ((d,) + MN[lg]) + s[m.end(1):]
    seg_start = m.start()
    ends = [x.start() for x in re.finditer(r'\n\s*(?:mr|hi|gu|pa|ta|te|kn): \{"', s) if x.start() > seg_start]
    seg_end = min(ends) if ends else len(s)
    s = setkey(s, "emp_details", t, seg_start, seg_end)
    s = setkey(s, "cmp_title", ck, seg_start, seg_end)
    s = setkey(s, "bill", mk, seg_start, seg_end)
rep('esc(tx("dl_pdf")) + \'</button><p class="msg" id="dmsg"', 'esc(tx("dl_mybill")) + \'</button><p class="msg" id="dmsg"')

# Make a Bill PDF made reusable
rep('  function makePdf() {\n    var b = billData, msg = $("pmsg");\n    if (!b) return;',
    '  function makePdf() { return makePdfFrom(billData, $("pmsg"), null); }\n  function makePdfFrom(b, msg, my) { /* BK-MYBILL */\n    if (!b) return;')
rep('var nameText = PS("Name") + ": " + (b.name || "____________________");', 'var nameText = my ? my.title : PS("Name") + ": " + (b.name || "____________________");')
rep('r.duty === "Half" ? "1" : "", r.duty === "Full" ? "1" : ""]; }),',
    'b.my ? (r.Half ? String(r.Half) : "") : (r.duty === "Half" ? "1" : ""), b.my ? (r.Full ? String(r.Full) : "") : (r.duty === "Full" ? "1" : "")]; }),')
rep('doc.roundedRect(14, y, W - 28, 78, 3, 3, "S");', 'doc.roundedRect(14, y, W - 28, my ? 48 : 78, 3, 3, "S");')
rep('PS("Half Days") + ": " + b.hd + "  (" + b.hd + " x " + money(b.rh) + " = " + money(b.hAmt) + ")"',
    'PS("Half Days") + ": " + b.hd + (b.rh === null ? "  (" + money(b.hAmt) + ")" : "  (" + b.hd + " x " + money(b.rh) + " = " + money(b.hAmt) + ")")')
rep('PS("Full Days") + ": " + b.fd + "  (" + b.fd + " x " + money(b.rf) + " = " + money(b.fAmt) + ")"',
    'PS("Full Days") + ": " + b.fd + (b.rf === null ? "  (" + money(b.fAmt) + ")" : "  (" + b.fd + " x " + money(b.rf) + " = " + money(b.fAmt) + ")")')
rep('    line(money(net1) + " + " + money(b.pend || 0) + " (" + PS("Pending payment") + ")", 20, y + 58, 12, false, ink);',
    '    if (!my) line(money(net1) + " + " + money(b.pend || 0) + " (" + PS("Pending payment") + ")", 20, y + 58, 12, false, ink);')
rep('line(PS("Final Payment") + " = " + money(b.net), 20, y + 68, 16, true, teal);', 'line(PS("Final Payment") + " = " + money(b.net), 20, y + (my ? 40 : 68), 16, true, teal);')
rep('''    var fname = (b.name.replace(/[^A-Za-z0-9]+/g, "-").replace(/^-|-$/g, "") || "Duty-Log") + "-bill.pdf";
    showPdfActions(fname, buf);''', '''    var fname = my ? my.fname : (b.name.replace(/[^A-Za-z0-9]+/g, "-").replace(/^-|-$/g, "") || "Duty-Log") + "-bill.pdf";
    showPdfActions(fname, buf, my ? my.box : undefined);''')

rep('    line(PS("Advance") + ": - " + money(b.adv), 20, y + 38, 12, false, ink);', '    if (!my) line(PS("Advance") + ": - " + money(b.adv), 20, y + 38, 12, false, ink);')
rep('    line(money(gross) + " - " + money(b.adv) + " = " + money(net1), 20, y + 47, 12, false, ink);', '    if (!my) line(money(gross) + " - " + money(b.adv) + " = " + money(net1), 20, y + 47, 12, false, ink);')
rep('<span data-i18n="bill">Make A Bill</span>', '<span data-i18n="bill">Make Employee\'s Bill</span>')
# My Bill card: the advance is not subtracted
rep('    state.employees.forEach(function (e) { total -= advTotal(e.id); });\n', '')
rep("""'</b></div><p class="dc-note">' + esc(tx("adv_subtracted")) + '</p></div>' +""", """'</b></div></div>' +""")
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
      adv: adv, net: hAmt + fAmt, pend: 0, advRows: advRows };
    makePdfFrom(b, $("dmsg"), { title: title, fname: title.replace(/[\\\\\\/:*?"<>|]+/g, "").trim() + ".pdf", box: "dacts" });
  }
''' + s[j:]

# Settings: manager name, typed once
card = '''<section id="p-set" hidden>
    <div class="card" id="mncard">
      <style>#mnsave:disabled{opacity:.4;cursor:not-allowed;filter:grayscale(.4)}</style>
      <h2 class="ratesh"><span class="ratesh-ic" aria-hidden="true"><svg viewBox="0 0 24 24"><circle cx="12" cy="8" r="3.8"/><path d="M4.5 20a7.5 7.5 0 0115 0"/></svg></span><span class="ratesh-t" data-i18n="mn_title">Manager Name</span></h2>
      <label for="mname" style="margin-top:0" data-i18n="mn_label">Your name (shown on My Total Bill PDF)</label>
      <input type="text" id="mname" maxlength="40" autocomplete="off" data-i18n-ph="mn_ph" placeholder="Enter manager name">
      <button class="btn save" id="mnsave" type="button" data-i18n="mn_save" disabled>Save name</button>
      <p class="msg" id="mnmsg" aria-live="polite"></p>
    </div>
'''
rep('<section id="p-set" hidden>\n', card)
rep('  function myName() {', '''  (function () {
    var inp = $("mname"); if (!inp) return;
    try { inp.value = localStorage.getItem("dutylog.mname") || ""; } catch (e) {}
    var sv = $("mnsave");
    function sync() { sv.disabled = !inp.value.trim(); }
    inp.addEventListener("input", sync); sync();
    $("mnsave").onclick = function () {
      var v = inp.value.trim(); inp.value = v; if (!v) { sync(); return; }
      try { localStorage.setItem("dutylog.mname", v); say($("mnmsg"), "Saved."); } catch (e) { say($("mnmsg"), "Could not save on this phone.", true); }
    };
  })();
  function myName() {''')
open(path, "w", encoding="utf-8").write(s)
print("mybill: patched")

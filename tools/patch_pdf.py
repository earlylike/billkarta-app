#!/usr/bin/env python3
"""App-only: bundles the PDF editor (github.com/earlylike/pdf) as www/pdf/ and adds a 'PDF Editor' card
to the Settings tab of Personal and Duty Manager (just above the Privacy & Contact card).

Usage: patch_pdf.py <assets/www folder> <folder with a clone of earlylike/pdf>
Idempotent. Limits: 2 MB file size, 10 pages. Run after patch_about.py."""
import json, os, re, shutil, sys

www, src = sys.argv[1], sys.argv[2]
MAX_MB, MAX_PAGES = 2, 10
URL = "../pdf/index.html"

# ------------------------------------------------------------------ 1) the editor page itself
out = os.path.join(www, "pdf")
os.makedirs(out, exist_ok=True)
shutil.copy(os.path.join(src, "style.css"), os.path.join(out, "style.css"))

js = open(os.path.join(src, "script.js"), encoding="utf-8").read()

# 1a) size check, loading hint and page limit; any failure restores the empty screen with a message
old_head = "$('file').onchange = async e => {\n  const f = e.target.files[0]; if (!f) return;\n"
assert js.count(old_head) == 1, "editor source changed: file handler not found"
new_head = ("const EMPTY_HTML = pagesEl.innerHTML;\n"
            "function resetEmpty() { pagesEl.innerHTML = EMPTY_HTML; pdfBytes = null; pdfPages = []; items = []; $('hint').textContent = ''; }\n"
            "const openPdfInner = async e => {\n  const f = e.target.files[0]; if (!f) return;\n"
            "  if (f.size > %d * 1024 * 1024) { e.target.value = ''; alert('File too big. The maximum PDF size is %d MB.'); return; }\n"
            "  $('hint').textContent = 'Loading PDF…';\n" % (MAX_MB, MAX_MB))
js = js.replace(old_head, new_head, 1)

old_doc = "  const pdf = await pdfjsLib.getDocument({ data: pdfBytes.slice() }).promise;\n  if (myLoad !== loadGen) return;\n"
assert js.count(old_doc) == 1, "editor source changed: getDocument not found"
new_doc = ("  const pdf = await pdfjsLib.getDocument({ data: pdfBytes.slice() }).promise;\n  if (myLoad !== loadGen) return;\n"
           "  if (pdf.numPages > %d) { e.target.value = ''; resetEmpty(); alert('Too many pages. The maximum is %d pages.'); return; }\n" % (MAX_PAGES, MAX_PAGES))
js = js.replace(old_doc, new_doc, 1)

old_end = "  setTool('edit');\n};\n\nfunction buildOrig"
assert js.count(old_end) == 1, "editor source changed: end of file handler not found"
new_end = ("  setTool('edit');\n};\n"
           "$('file').onchange = async e => {\n"
           "  try { await openPdfInner(e); e.target.value = ''; }\n"
           "  catch (err) { resetEmpty(); e.target.value = ''; alert('Could not open this PDF. It may be damaged or password protected.'); }\n"
           "};\n\nfunction buildOrig")
js = js.replace(old_end, new_end, 1)
for a, b in (("Click any existing text", "Tap any existing text"), ("Click on page to add text", "Tap on page to add text")):
    js = js.replace(a, b)
open(os.path.join(out, "script.js"), "w", encoding="utf-8").write(js)

# 1b) index.html: offline shim (saves PDFs to the phone), toast instead of alert(), back button
html = open(os.path.join(src, "index.html"), encoding="utf-8").read()
html = html.replace("<title>PDF Editor</title>", "<title>PDF Editor</title>\n<script src=\"/assets/www/app-shim.js\"></script>", 1)
html = html.replace('<div id="bar">\n', '<div id="bar">\n  <button id="backBtn" type="button" aria-label="Back" onclick="history.length>1?history.back():(location.href=\'../Work/index.html\')">‹ Back</button>\n', 1)
extra = """
<div id="bkBrand">Sponsored by BillKarta</div>
<div id="bkToast" role="status" aria-live="polite"></div>
<style>
#backBtn{height:42px;padding:0 14px;border-radius:12px;border:1px solid rgba(255,255,255,.25);background:rgba(255,255,255,.08);color:#fff;font:600 14px/1 system-ui,sans-serif;flex:none}
#hint{flex:1 1 100% !important;order:9 !important;min-width:0}
#bkBrand{position:fixed;left:14px;bottom:calc(10px + env(safe-area-inset-bottom,0px));font:500 10px/1 'Poppins',system-ui,sans-serif;letter-spacing:.3px;color:rgba(245,230,197,.55);pointer-events:none;z-index:5}
#bkToast{position:fixed;left:50%;bottom:calc(24px + env(safe-area-inset-bottom,0px));transform:translate(-50%,20px);max-width:88vw;padding:12px 18px;border-radius:14px;background:#1b1e26;color:#fff;border:1px solid rgba(255,255,255,.2);box-shadow:0 10px 30px rgba(0,0,0,.5);font:500 14px/1.4 system-ui,sans-serif;text-align:center;opacity:0;pointer-events:none;transition:opacity .2s,transform .2s;z-index:9999}
#bkToast.show{opacity:1;transform:translate(-50%,0)}
</style>
<script>
/* WebView hides alert(); show a toast instead */
window.alert = function (m) {
  var t = document.getElementById('bkToast'); t.textContent = String(m); t.classList.add('show');
  clearTimeout(window.__bkT); window.__bkT = setTimeout(function () { t.classList.remove('show'); }, 4200);
};
</script>
"""
html = html.replace("</body>", extra + "</body>", 1)
html = html.replace("Click “Open PDF” to load a file.", "Tap “Open PDF” to load a file.", 1)
html = html.replace("Everything runs in your browser — nothing is uploaded.",
                    "Max %d MB and %d pages. Everything stays on your phone — nothing is uploaded." % (MAX_MB, MAX_PAGES), 1)
open(os.path.join(out, "index.html"), "w", encoding="utf-8").write(html)
print("pdf editor bundled")

# ------------------------------------------------------------------ 2) Settings card
T = {
 "en": ("PDF Editor", "Open a PDF from your phone, edit the text and save a new copy. Works offline. Up to %d MB and %d pages." % (MAX_MB, MAX_PAGES), "Open PDF Editor"),
 "hi": ("पीडीएफ एडिटर", "अपने फ़ोन से PDF खोलें, टेक्स्ट बदलें और नई कॉपी सेव करें। ऑफ़लाइन चलता है। अधिकतम %d MB और %d पेज।" % (MAX_MB, MAX_PAGES), "PDF एडिटर खोलें"),
 "mr": ("पीडीएफ एडिटर", "फोनमधील PDF उघडा, मजकूर बदला आणि नवीन प्रत जतन करा. ऑफलाइन चालते. कमाल %d MB आणि %d पाने." % (MAX_MB, MAX_PAGES), "PDF एडिटर उघडा"),
 "gu": ("પીડીએફ એડિટર", "ફોનમાંથી PDF ખોલો, લખાણ બદલો અને નવી નકલ સાચવો. ઑફલાઇન ચાલે છે. વધુમાં વધુ %d MB અને %d પાનાં." % (MAX_MB, MAX_PAGES), "PDF એડિટર ખોલો"),
 "pa": ("ਪੀਡੀਐਫ ਐਡੀਟਰ", "ਫ਼ੋਨ ਤੋਂ PDF ਖੋਲ੍ਹੋ, ਲਿਖਤ ਬਦਲੋ ਅਤੇ ਨਵੀਂ ਕਾਪੀ ਸੇਵ ਕਰੋ। ਔਫ਼ਲਾਈਨ ਚੱਲਦਾ ਹੈ। ਵੱਧ ਤੋਂ ਵੱਧ %d MB ਅਤੇ %d ਪੰਨੇ।" % (MAX_MB, MAX_PAGES), "PDF ਐਡੀਟਰ ਖੋਲ੍ਹੋ"),
 "ta": ("PDF எடிட்டர்", "போனிலிருந்து PDF ஐத் திறந்து, உரையை மாற்றி, புதிய நகலைச் சேமிக்கவும். ஆஃப்லைனில் வேலை செய்யும். அதிகபட்சம் %d MB மற்றும் %d பக்கங்கள்." % (MAX_MB, MAX_PAGES), "PDF எடிட்டரைத் திற"),
 "te": ("PDF ఎడిటర్", "ఫోన్ నుండి PDF తెరిచి, టెక్స్ట్ మార్చి, కొత్త కాపీని సేవ్ చేయండి. ఆఫ్‌లైన్‌లో పని చేస్తుంది. గరిష్టంగా %d MB మరియు %d పేజీలు." % (MAX_MB, MAX_PAGES), "PDF ఎడిటర్ తెరవండి"),
 "kn": ("PDF ಎಡಿಟರ್", "ಫೋನ್‌ನಿಂದ PDF ತೆರೆಯಿರಿ, ಪಠ್ಯ ಬದಲಿಸಿ ಮತ್ತು ಹೊಸ ಪ್ರತಿಯನ್ನು ಉಳಿಸಿ. ಆಫ್‌ಲೈನ್‌ನಲ್ಲಿ ಕೆಲಸ ಮಾಡುತ್ತದೆ. ಗರಿಷ್ಠ %d MB ಮತ್ತು %d ಪುಟಗಳು." % (MAX_MB, MAX_PAGES), "PDF ಎಡಿಟರ್ ತೆರೆಯಿರಿ"),
}

CSS = """
/* BK-PDFCARD */
#pdfcard{--tint:#fde9c9}
#pdfcard .pdf-h{font-size:1.2rem;font-weight:800;margin:0 0 .45rem}
#pdfcard .pdf-p{margin:0 0 .9rem;font-size:.95rem;color:var(--muted)}
#pdfcard a.pdf-go{display:block;text-align:center;padding:.8rem 1rem;border-radius:14px;
  font-weight:700;font-size:.95rem;text-decoration:none;color:var(--ink);background:var(--card);border:1px solid var(--line)}
"""

def card(h, p, b, i18n):
    a = (lambda k: ' data-i18n="%s"' % k) if i18n else (lambda k: "")
    return ('    <div class="card" id="pdfcard">\n'
            '      <h2 class="pdf-h"%s>%s</h2>\n'
            '      <p class="pdf-p"%s>%s</p>\n'
            '      <a class="pdf-go" href="%s"%s>%s</a>\n'
            '    </div>\n') % (a("pdf_t"), h, a("pdf_p"), p, URL, a("pdf_b"), b)

def add_css(s):
    j = s.rfind("</style>")
    return s[:j] + CSS + s[j:]

MARK = '    <div class="card" id="aboutcard">'

# Personal (Work): translated by matching the English text
p = os.path.join(www, "Work", "index.html")
s = open(p, encoding="utf-8").read()
if 'id="pdfcard"' not in s:
    extra = ""
    for idx in range(3):
        extra += json.dumps(T["en"][idx], ensure_ascii=False) + ":" + json.dumps(
            {k: v[idx] for k, v in T.items() if k != "en"}, ensure_ascii=False) + ","
    assert s.count("var I18N_S = {") == 1
    s = s.replace("var I18N_S = {", "var I18N_S = {" + extra, 1)
    assert s.count(MARK) == 1
    e = T["en"]
    s = s.replace(MARK, card(e[0], e[1], e[2], False) + MARK, 1)
    s = add_css(s)
    open(p, "w", encoding="utf-8").write(s)
    print("patched Work pdf card")
else:
    print("Work pdf card already patched")

# Duty Manager (forall): data-i18n keys in every language block
p = os.path.join(www, "forall", "index.html")
s = open(p, encoding="utf-8").read()
if 'id="pdfcard"' not in s:
    for lang, (h, t, b) in T.items():
        pat = re.compile(r'((?:\n\s*|var I18N = \{\s*)%s: \{.*?"about_c": "[^"]*")' % lang, re.S)
        m = pat.search(s)
        assert m, lang
        add = ', "pdf_t": %s, "pdf_p": %s, "pdf_b": %s' % tuple(json.dumps(x, ensure_ascii=False) for x in (h, t, b))
        s = s[:m.end()] + add + s[m.end():]
    assert s.count(MARK) == 1
    e = T["en"]
    s = s.replace(MARK, card(e[0], e[1], e[2], True) + MARK, 1)
    s = add_css(s)
    open(p, "w", encoding="utf-8").write(s)
    print("patched forall pdf card")
else:
    print("forall pdf card already patched")

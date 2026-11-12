#!/usr/bin/env python3
"""App-only wording change for the Duty form (Personal + Duty Manager pages):
   label  -> "Location/Work"
   hint   -> "Enter Location or Work"
Table headings and PDFs keep the word "Location".
Usage: patch_location.py <assets/www folder>   (idempotent; run by sync-pages.sh)"""
import json, re, sys, os

root = sys.argv[1]

LABEL = {"en": "Location/Work", "hi": "जगह/काम", "mr": "ठिकाण/काम", "gu": "સ્થળ/કામ",
         "pa": "ਥਾਂ/ਕੰਮ", "ta": "இடம்/வேலை", "te": "స్థలం/పని", "kn": "ಸ್ಥಳ/ಕೆಲಸ"}
HINT = {"en": "Enter Location or Work", "hi": "जगह या काम लिखें", "mr": "ठिकाण किंवा काम लिहा",
        "gu": "સ્થળ અથવા કામ લખો", "pa": "ਥਾਂ ਜਾਂ ਕੰਮ ਲਿਖੋ", "ta": "இடம் அல்லது வேலையை உள்ளிடவும்",
        "te": "స్థలం లేదా పని నమోదు చేయండి", "kn": "ಸ್ಥಳ ಅಥವಾ ಕೆಲಸ ನಮೂದಿಸಿ"}

def q(s):
    return json.dumps(s, ensure_ascii=False)

# ---------- Personal page (Work) ----------
p = os.path.join(root, "Work", "index.html")
s = open(p, encoding="utf-8").read()
if "Location/Work" not in s:
    extra = ('"Location/Work":' + json.dumps({k: v for k, v in LABEL.items() if k != "en"}, ensure_ascii=False) +
             ',"Enter Location or Work":' + json.dumps({k: v for k, v in HINT.items() if k != "en"}, ensure_ascii=False) + ',')
    assert s.count("var I18N_S = {") == 1
    s = s.replace("var I18N_S = {", "var I18N_S = {" + extra, 1)
    n1 = s.count(">Location of duty</label>")
    s = s.replace(">Location of duty</label>", ">Location/Work</label>")
    n2 = s.count('placeholder="For example: Nandu Bhavan"')
    s = s.replace('placeholder="For example: Nandu Bhavan"', 'placeholder="Enter Location or Work"')
    assert n1 == 2 and n2 == 2, (n1, n2)
    open(p, "w", encoding="utf-8").write(s)
    print("patched Work")
else:
    print("Work already patched")

# ---------- Duty Manager page (forall) ----------
p = os.path.join(root, "forall", "index.html")
s = open(p, encoding="utf-8").read()
if '"location_work"' not in s:
    for lang in LABEL:
        pat = re.compile(r'((?:\n\s*|var I18N = \{\s*)%s: \{.*?)"loc_ph":\s*"[^"]*"' % lang, re.S)
        m = pat.search(s)
        assert m, lang
        s = s[:m.start()] + m.group(1) + '"loc_ph": ' + q(HINT[lang]) + ', "location_work": ' + q(LABEL[lang]) + s[m.end():]
    n = s.count('<label for="loc" data-i18n="location">Location</label>') + s.count('<label for="eloc" data-i18n="location">Location</label>')
    assert n == 2, n
    s = s.replace('<label for="loc" data-i18n="location">Location</label>', '<label for="loc" data-i18n="location_work">Location/Work</label>')
    s = s.replace('<label for="eloc" data-i18n="location">Location</label>', '<label for="eloc" data-i18n="location_work">Location/Work</label>')
    s = s.replace('placeholder="Where was the duty?"', 'placeholder="Enter Location or Work"')
    open(p, "w", encoding="utf-8").write(s)
    print("patched forall")
else:
    print("forall already patched")

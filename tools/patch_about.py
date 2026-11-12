#!/usr/bin/env python3
"""App-only: adds a 'Privacy & Contact' card at the bottom of the Settings tab (Personal + Duty Manager).
Usage: patch_about.py <assets/www folder>   (idempotent; run by sync-pages.sh, after patch_location.py)"""
import json, os, re, sys

root = sys.argv[1]
POLICY_URL = "https://earlylike.github.io/billkarta-app/privacy.html"
EMAIL = "gurulinggaidhankar@gmail.com"

T = {  # title, text, privacy button, contact button
 "en": ("Privacy & Contact", "Your data stays on this phone. We do not collect or share it.", "Privacy Policy", "Contact us"),
 "hi": ("गोपनीयता और संपर्क", "आपका डेटा इसी फ़ोन में रहता है। हम इसे इकट्ठा या साझा नहीं करते।", "गोपनीयता नीति", "हमसे संपर्क करें"),
 "mr": ("गोपनीयता आणि संपर्क", "तुमचा डेटा याच फोनमध्ये राहतो. आम्ही तो गोळा किंवा शेअर करत नाही.", "गोपनीयता धोरण", "आमच्याशी संपर्क साधा"),
 "gu": ("ગોપનીયતા અને સંપર્ક", "તમારો ડેટા આ ફોનમાં જ રહે છે. અમે તેને એકત્ર કે શેર કરતા નથી.", "ગોપનીયતા નીતિ", "અમારો સંપર્ક કરો"),
 "pa": ("ਪਰਦੇਦਾਰੀ ਅਤੇ ਸੰਪਰਕ", "ਤੁਹਾਡਾ ਡਾਟਾ ਇਸੇ ਫ਼ੋਨ ਵਿੱਚ ਰਹਿੰਦਾ ਹੈ। ਅਸੀਂ ਇਸਨੂੰ ਇਕੱਠਾ ਜਾਂ ਸਾਂਝਾ ਨਹੀਂ ਕਰਦੇ।", "ਪਰਦੇਦਾਰੀ ਨੀਤੀ", "ਸਾਡੇ ਨਾਲ ਸੰਪਰਕ ਕਰੋ"),
 "ta": ("தனியுரிமை மற்றும் தொடர்பு", "உங்கள் தரவு இந்த போனிலேயே இருக்கும். நாங்கள் அதை சேகரிக்கவோ பகிரவோ மாட்டோம்.", "தனியுரிமைக் கொள்கை", "எங்களைத் தொடர்பு கொள்ள"),
 "te": ("గోప్యత మరియు సంప్రదింపు", "మీ డేటా ఈ ఫోన్‌లోనే ఉంటుంది. మేము దానిని సేకరించము లేదా పంచుకోము.", "గోప్యతా విధానం", "మమ్మల్ని సంప్రదించండి"),
 "kn": ("ಗೌಪ್ಯತೆ ಮತ್ತು ಸಂಪರ್ಕ", "ನಿಮ್ಮ ಡೇಟಾ ಈ ಫೋನ್‌ನಲ್ಲಿಯೇ ಇರುತ್ತದೆ. ನಾವು ಅದನ್ನು ಸಂಗ್ರಹಿಸುವುದಿಲ್ಲ ಅಥವಾ ಹಂಚಿಕೊಳ್ಳುವುದಿಲ್ಲ.", "ಗೌಪ್ಯತಾ ನೀತಿ", "ನಮ್ಮನ್ನು ಸಂಪರ್ಕಿಸಿ"),
}

CSS = """
/* BK-ABOUT */
#aboutcard{--tint:#e4defc}
#aboutcard .about-h{font-size:1.2rem;font-weight:800;margin:0 0 .45rem}
#aboutcard .about-p{margin:0 0 .9rem;font-size:.95rem;color:var(--muted)}
#aboutcard .about-actions{display:flex;gap:.6rem;flex-wrap:wrap}
#aboutcard .about-actions a{flex:1;min-width:9rem;text-align:center;padding:.8rem 1rem;border-radius:14px;
  font-weight:700;font-size:.95rem;text-decoration:none;color:var(--ink);background:var(--card);border:1px solid var(--line)}
"""

def card(h, p, b1, b2, i18n):
    a = (lambda k: ' data-i18n="%s"' % k) if i18n else (lambda k: "")
    return ('\n    <div class="card" id="aboutcard">\n'
            '      <h2 class="about-h"%s>%s</h2>\n'
            '      <p class="about-p"%s>%s</p>\n'
            '      <div class="about-actions">\n'
            '        <a href="%s"%s>%s</a>\n'
            '        <a href="mailto:%s"%s>%s</a>\n'
            '      </div>\n    </div>\n') % (
        a("about_t"), h.replace("&", "&amp;"), a("about_p"), p,
        POLICY_URL, a("about_pp"), b1, EMAIL, a("about_c"), b2)

def insert_after_div(s, start_marker, html):
    i = s.index(start_marker)
    pos = i
    depth = 0
    for m in re.finditer(r"<div\b|</div>", s[i:]):
        depth += 1 if m.group(0).startswith("<div") else -1
        if depth == 0:
            pos = i + m.end()
            break
    return s[:pos] + html + s[pos:]

def add_css(s):
    j = s.rfind("</style>")
    return s[:j] + CSS + s[j:]

# ---------- Personal page ----------
p = os.path.join(root, "Work", "index.html")
s = open(p, encoding="utf-8").read()
if 'id="aboutcard"' not in s:
    extra = ""
    for idx, key in enumerate(("Privacy & Contact", "Your data stays on this phone. We do not collect or share it.",
                               "Privacy Policy", "Contact us")):
        extra += json.dumps(key, ensure_ascii=False) + ":" + json.dumps(
            {k: v[idx] for k, v in T.items() if k != "en"}, ensure_ascii=False) + ","
    assert s.count("var I18N_S = {") == 1
    s = s.replace("var I18N_S = {", "var I18N_S = {" + extra, 1)
    e = T["en"]
    s = insert_after_div(s, '<div class="card" id="trashcard">', card(e[0], e[1], e[2], e[3], False))
    s = add_css(s)
    open(p, "w", encoding="utf-8").write(s)
    print("patched Work about card")
else:
    print("Work about card already patched")

# ---------- Duty Manager page ----------
p = os.path.join(root, "forall", "index.html")
s = open(p, encoding="utf-8").read()
if 'id="aboutcard"' not in s:
    for lang, (h, t, b1, b2) in T.items():
        pat = re.compile(r'((?:\n\s*|var I18N = \{\s*)%s: \{.*?"location_work": "[^"]*")' % lang, re.S)
        m = pat.search(s)
        assert m, lang
        add = (', "about_t": %s, "about_p": %s, "about_pp": %s, "about_c": %s' % (
            json.dumps(h, ensure_ascii=False), json.dumps(t, ensure_ascii=False),
            json.dumps(b1, ensure_ascii=False), json.dumps(b2, ensure_ascii=False)))
        s = s[:m.end()] + add + s[m.end():]
    e = T["en"]
    s = insert_after_div(s, '<div class="card" id="langcard">', card(e[0], e[1], e[2], e[3], True))
    s = add_css(s)
    open(p, "w", encoding="utf-8").write(s)
    print("patched forall about card")
else:
    print("forall about card already patched")

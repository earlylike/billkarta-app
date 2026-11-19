#!/usr/bin/env python3
"""App-only: adds a language button below the BillKarta container on the front page.
Tapping it opens a popup with the 8 languages. The choice is saved under the same key the Personal and
Duty Manager pages already read ('dutylog.lang'), so both pages open in the chosen language.
Usage: patch_frontpage_lang.py <assets/www folder>   (idempotent)"""
import os, sys

p = os.path.join(sys.argv[1], "frontpage", "index.html")
s = open(p, encoding="utf-8").read()
if "BK-LANG" in s:
    print("frontpage language button already patched")
    sys.exit(0)

CSS = """<style>/* BK-LANG */
body{flex-direction:column;gap:18px}
.bk-lp{display:flex;align-items:center;gap:8px;padding:10px 20px;border-radius:999px;background:rgba(8,10,14,.78);border:1px solid rgba(198,156,80,.6);color:#f4d58d;font:600 13px/1 'Poppins',system-ui,sans-serif;box-shadow:0 8px 24px rgba(0,0,0,.45);cursor:pointer;position:relative;z-index:1;-webkit-tap-highlight-color:transparent}
.bk-lp .g{font-size:15px}.bk-lp .c{font-size:12px;opacity:.9}
.bk-ov{position:fixed;inset:0;background:rgba(0,0,0,.62);-webkit-backdrop-filter:blur(3px);backdrop-filter:blur(3px);display:none;align-items:center;justify-content:center;padding:22px;z-index:99}
.bk-ov.show{display:flex}
.bk-pop{width:100%;max-width:340px;max-height:92vh;display:flex;flex-direction:column;border-radius:24px;background:linear-gradient(160deg,#1d1a12,#101216 55%);border:1px solid rgba(198,156,80,.55);box-shadow:0 30px 80px rgba(0,0,0,.7);padding:20px 16px 16px;font-family:'Poppins',system-ui,sans-serif}
.bk-ph{text-align:center;margin-bottom:12px}
.bk-gi{width:46px;height:46px;margin:0 auto 8px;border-radius:14px;display:flex;align-items:center;justify-content:center;font-size:23px;background:linear-gradient(135deg,#f5d990,#b88935)}
.bk-pop h3{font-size:16px;font-weight:600;color:#f5e6c5;margin:0}.bk-pop p{font-size:11px;color:#99958c;margin:3px 0 0}
.bk-pl{overflow:auto;margin-top:12px;border-radius:16px;border:1px solid rgba(255,255,255,.08);background:rgba(255,255,255,.03);min-height:0}
.bk-pi{display:flex;align-items:center;gap:12px;padding:12px 14px;border-bottom:1px solid rgba(255,255,255,.06);color:#f5e6c5;font-size:15px;cursor:pointer;-webkit-tap-highlight-color:transparent}
.bk-pi:last-child{border-bottom:0}.bk-pi small{margin-left:auto;font-size:11px;color:#99958c}
.bk-rd{width:18px;height:18px;border-radius:50%;border:2px solid #6f685a;flex-shrink:0}
.bk-pi.on{background:rgba(218,177,91,.14);color:#f4d58d;font-weight:600}.bk-pi.on .bk-rd{border-color:#f4d58d;background:radial-gradient(circle,#f4d58d 45%,transparent 50%)}
.bk-pb{margin-top:14px;width:100%;padding:12px;border:0;border-radius:14px;text-align:center;font:600 14px 'Poppins',system-ui,sans-serif;color:#1a1405;background:linear-gradient(135deg,#f5d990,#b88935);cursor:pointer}
</style>
"""

PILL = '<button type="button" class="bk-lp" id="bkLangBtn" aria-haspopup="dialog"><span class="g">🌐</span><span id="bkLangName">English</span><span class="c">⌄</span></button>\n'

POPUP = """<div class="bk-ov" id="bkLangOv" role="dialog" aria-modal="true" aria-labelledby="bkLangT">
  <div class="bk-pop">
    <div class="bk-ph"><div class="bk-gi">🌐</div><h3 id="bkLangT">Choose your language</h3><p>You can change it later in Settings</p></div>
    <div class="bk-pl" id="bkLangList"></div>
    <button type="button" class="bk-pb" id="bkLangOk">Continue</button>
  </div>
</div>
<script>/* BK-LANG */
(function () {
  var KEY = 'dutylog.lang';
  var L = [['en','English','English'],['hi','हिन्दी','Hindi'],['mr','मराठी','Marathi'],['gu','ગુજરાતી','Gujarati'],
           ['pa','ਪੰਜਾਬੀ','Punjabi'],['ta','தமிழ்','Tamil'],['te','తెలుగు','Telugu'],['kn','ಕನ್ನಡ','Kannada']];
  var mem = 'en', cur;
  function load() { try { var v = localStorage.getItem(KEY); if (L.some(function (x) { return x[0] === v; })) return v; } catch (e) {} return mem; }
  function save(v) { mem = v; try { localStorage.setItem(KEY, v); } catch (e) {} }
  function name(code) { for (var i = 0; i < L.length; i++) if (L[i][0] === code) return L[i][1]; return 'English'; }
  var ov = document.getElementById('bkLangOv'), list = document.getElementById('bkLangList'), btn = document.getElementById('bkLangBtn');
  function label() { document.getElementById('bkLangName').textContent = name(load()); }
  function draw() {
    list.innerHTML = '';
    L.forEach(function (x) {
      var d = document.createElement('div'); d.className = 'bk-pi' + (x[0] === cur ? ' on' : ''); d.setAttribute('role', 'option');
      d.innerHTML = '<span class="bk-rd"></span>' + x[1] + (x[0] === 'en' ? '' : '<small>' + x[2] + '</small>');
      d.onclick = function () { cur = x[0]; draw(); };
      list.appendChild(d);
    });
  }
  function open() { cur = load(); draw(); ov.classList.add('show'); try { history.pushState({ bkLang: 1 }, ''); } catch (e) {} }
  function close() { if (!ov.classList.contains('show')) return; ov.classList.remove('show'); }
  function closeUi() { close(); try { if (history.state && history.state.bkLang) history.back(); } catch (e) {} }
  btn.onclick = open;
  document.getElementById('bkLangOk').onclick = function () { save(cur); label(); closeUi(); };
  ov.onclick = function (e) { if (e.target === ov) closeUi(); };
  window.addEventListener('popstate', close);
  label();
})();
</script>
"""

assert s.count("</main>") == 1 and s.count("</body>") == 1 and s.count("</head>") == 1
s = s.replace("</head>", CSS + "</head>", 1)
s = s.replace("</main>", "</main>\n" + PILL, 1)
s = s.replace("</body>", POPUP + "</body>", 1)
open(p, "w", encoding="utf-8").write(s)
print("patched frontpage language button")

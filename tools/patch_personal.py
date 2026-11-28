#!/usr/bin/env python3
"""Personal page (Work) only. Run after patch_social.py.
 - Settings: separate 'My Name' card (Save name disabled until a name is typed) + 'Rates' card renamed 'My Daily Payment'
 - Adding a duty or an advance without a saved name sends the user to the My Name card (scroll, focus, highlight 3 times)"""
import json, os, sys
root = sys.argv[1]
fp = os.path.join(root, "Work", "index.html")
f = open(fp, encoding="utf-8").read()
if "BK-MYNAME" in f:
    print("personal: already patched"); sys.exit(0)

def rep(a, b, n=1):
    global f
    assert f.count(a) == n, (f.count(a), a[:100])
    f = f.replace(a, b)

TR = {
 "My Name": ["माझे नाव", "मेरा नाम", "મારું નામ", "ਮੇਰਾ ਨਾਂ", "என் பெயர்", "నా పేరు", "ನನ್ನ ಹೆಸರು"],
 "Save name": ["नाव जतन करा", "नाम सेव करें", "નામ સાચવો", "ਨਾਂ ਸੰਭਾਲੋ", "பெயரைச் சேமி", "పేరు సేవ్ చేయండి", "ಹೆಸರು ಉಳಿಸಿ"],
 "My Daily Payment": ["माझे दैनिक पेमेंट", "मेरा दैनिक भुगतान", "મારી દૈનિક ચુકવણી", "ਮੇਰਾ ਰੋਜ਼ਾਨਾ ਭੁਗਤਾਨ", "என் தினசரி கட்டணம்", "నా రోజువారీ చెల్లింపు", "ನನ್ನ ದೈನಂದಿನ ಪಾವತಿ"],
 "Name saved.": ["नाव जतन झाले.", "नाम सेव हो गया।", "નામ સાચવ્યું.", "ਨਾਂ ਸੰਭਾਲਿਆ ਗਿਆ।", "பெயர் சேமிக்கப்பட்டது.", "పేరు సేవ్ అయింది.", "ಹೆಸರು ಉಳಿಸಲಾಗಿದೆ."],
 "Enter your name and tap Save name first.": ["आधी तुमचे नाव लिहा आणि ‘नाव जतन करा’ दाबा.", "पहले अपना नाम लिखें और ‘नाम सेव करें’ दबाएँ।", "પહેલા તમારું નામ લખો અને ‘નામ સાચવો’ દબાવો.", "ਪਹਿਲਾਂ ਆਪਣਾ ਨਾਂ ਲਿਖੋ ਅਤੇ ‘ਨਾਂ ਸੰਭਾਲੋ’ ਦਬਾਓ।", "முதலில் உங்கள் பெயரை உள்ளிட்டு ‘பெயரைச் சேமி’ என்பதை அழுத்தவும்.", "ముందుగా మీ పేరు నమోదు చేసి ‘పేరు సేవ్ చేయండి’ నొక్కండి.", "ಮೊದಲು ನಿಮ್ಮ ಹೆಸರು ನಮೂದಿಸಿ ಮತ್ತು ‘ಹೆಸರು ಉಳಿಸಿ’ ಒತ್ತಿ."],
}
LG = ["mr", "hi", "gu", "pa", "ta", "te", "kn"]
ins = ""
for k, v in TR.items():
    assert '"%s":{' % k not in f, k
    ins += json.dumps(k, ensure_ascii=False) + ":" + json.dumps(dict(zip(LG, v)), ensure_ascii=False, separators=(",", ":")) + ","
rep("var I18N_S = {", "var I18N_S = {" + ins)

# HTML: My Name card, rates card without the name field
USER = '<svg viewBox="0 0 24 24"><circle cx="12" cy="8" r="3.8"/><path d="M4.5 20a7.5 7.5 0 0115 0"/></svg>'
rep('''<label class="lbl" for="name">Your name</label>
    <input type="text" class="name" id="name" maxlength="60" autocomplete="name" placeholder="Enter your name">
''', "")
rep('<span class="ratesh-t">Rates</span></h2>', '<span class="ratesh-t">My Daily Payment</span></h2>')
rep('<div class="card" id="ratescard">', '''<div class="card" id="mycard"><!-- BK-MYNAME -->
    <h2 class="ratesh"><span class="ratesh-ic" aria-hidden="true">%s</span><span class="ratesh-t">My Name</span></h2>
    <label class="lbl" for="name">Your name</label>
    <input type="text" class="name" id="name" maxlength="60" autocomplete="name" placeholder="Enter your name">
    <button type="button" class="btn" id="n-save" disabled>Save name</button>
    <p class="msg" id="n-msg" role="status" aria-live="polite"></p>
  </div>
<div class="card" id="ratescard">''' % USER)
rep("#ratescard{--tint:#fde3cf}", "#ratescard{--tint:#fde3cf}#mycard{--tint:#e4defc}#mycard .btn{width:100%;margin-top:1rem}@keyframes mcpulse{0%,100%{box-shadow:0 0 0 0 rgba(251,191,36,0);transform:none}50%{box-shadow:0 0 0 7px rgba(251,191,36,.85);transform:scale(1.015)}}#mycard.mcflash{animation:mcpulse .7s ease-in-out 3}")

# the name is saved only with the Save name button
rep('''  nameEl.addEventListener('input', function(){
    try { localStorage.setItem('dutyName', nameEl.value.trim()); } catch (err) {}
''', '''  nameEl.addEventListener('input', function(){
''')

JS = r'''
  /* BK-MYNAME: name card, Save name, and the redirect when a name is missing */
  var nSave = document.getElementById('n-save'), nMsg = document.getElementById('n-msg'), myNameSaved = nameEl.value.trim();
  function savedName(){ try { return (localStorage.getItem('dutyName') || '').trim(); } catch (err) { return myNameSaved; } }
  function nSay(t, bad){ nMsg.textContent = t; nMsg.className = 'msg' + (bad ? ' err' : ''); }
  function syncNameBtn(){ nSave.disabled = !nameEl.value.trim(); }
  nameEl.addEventListener('input', function(){ syncNameBtn(); nSay('', false); });
  syncNameBtn();
  nSave.addEventListener('click', function(){
    var v = nameEl.value.trim(); if (!v) return;
    try { localStorage.setItem('dutyName', v); } catch (err) {}
    myNameSaved = v; updateWho(); updateWa(); nSay(S('Name saved.'), false);
  });
  function needName(ev){
    if (savedName()) return false;
    if (ev) { ev.preventDefault(); ev.stopImmediatePropagation(); }
    document.querySelector('.tab[data-tab="set"]').click();
    setTimeout(function(){
      var c = document.getElementById('mycard');
      c.scrollIntoView({block: 'center'});
      c.classList.remove('mcflash'); void c.offsetWidth; c.classList.add('mcflash');
      try { nameEl.focus({preventScroll: true}); } catch (err) {}
      nSay(S('Enter your name and tap Save name first.'), true);
    }, 80);
    return true;
  }
  document.getElementById('save-duty').addEventListener('click', needName, true);
  document.getElementById('form').addEventListener('submit', needName, true);
  document.getElementById('a-add').addEventListener('click', needName, true);
'''
rep("  loadLang();\n  applyStatic();", JS + "  loadLang();\n  applyStatic();")
open(fp, "w", encoding="utf-8").write(f)
print("personal: patched")

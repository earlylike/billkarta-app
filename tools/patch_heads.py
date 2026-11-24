#!/usr/bin/env python3
"""Duty Manager only: Head Of Manager. Run AFTER patch_mybill.py (and after patch_mom, so the Manager of Managers page is not touched).
 - Settings: Head Of Manager card (add / update / delete -> Trash, restore from Trash)
 - Add Duty / Update duty: compulsory "Select Head Of Manager" (popup list), saved with each duty, shown under the date in Saved duties
 - My Total Bill: head textbox with suggestions; only that head's duties; PDF gets the head's name in the top-right corner
 - Backup keeps heads. All texts in 8 languages."""
import json, os, re, sys
root = sys.argv[1]
fp = os.path.join(root, "forall", "index.html")
f = open(fp, encoding="utf-8").read()
if "BK-HEADS" in f:
    print("heads: already patched"); sys.exit(0)

def rep(a, b, n=1):
    global f
    assert f.count(a) == n, (f.count(a), a[:90])
    f = f.replace(a, b)

# ---------- state / load ----------
rep("var state = { employees: [], records: [], advances: [], trash: [] };", "var state = { employees: [], records: [], advances: [], trash: [], heads: [] };")
rep("if (!state.trash) state.trash = []; if (!state.pending) state.pending = {};", "if (!state.trash) state.trash = []; if (!state.heads) state.heads = []; if (!state.pending) state.pending = {};")

# ---------- Settings card (after Manager Name card) ----------
HM_CARD = '''
    <div class="card" id="hmcard"><!-- BK-HEADS -->
      <style>#hmadd:disabled{opacity:.4;cursor:not-allowed;filter:grayscale(.4)}#hmlist .erow .avatar{flex:none}</style>
      <h2 class="ratesh"><span class="ratesh-ic" aria-hidden="true"><svg viewBox="0 0 24 24"><circle cx="12" cy="7.5" r="3.3"/><path d="M5 20a7 7 0 0114 0"/><path d="M9 3.2l1.6 1.4L12 2.6l1.4 2 1.6-1.4"/></svg></span><span class="ratesh-t" data-i18n="hm_title">Head Of Manager</span></h2>
      <label for="hmname" style="margin-top:0" data-i18n="hm_label">Add Head Of Manager</label>
      <input type="text" id="hmname" maxlength="40" autocomplete="off" data-i18n-ph="hm_ph" placeholder="Ex. Shelar sir">
      <button class="btn" id="hmadd" type="button" data-i18n="hm_add" disabled>Add Head Of Manager</button>
      <p class="msg" id="hmmsg" aria-live="polite"></p>
      <div id="hmlist" style="margin-top:.9rem"></div>
    </div>
'''
i = f.index('id="mncard"')
j = f.index("\n    </div>\n", i) + len("\n    </div>\n")
f = f[:j] + HM_CARD + f[j:]

# ---------- Add Duty: Select Head Of Manager ----------
SEL = '''<label id="hsl" data-i18n="hm_sel">Select Head Of Manager</label>
      <div style="position:relative"><input type="text" id="hsel" readonly data-i18n-ph="hm_sel_ph" placeholder="Example - Shelar sir" style="padding-right:44px;cursor:pointer" autocomplete="off"><svg viewBox="0 0 24 24" width="20" height="20" aria-hidden="true" style="position:absolute;right:14px;top:50%;transform:translateY(-50%);fill:none;stroke:#4338ca;stroke-width:2.4;stroke-linecap:round;stroke-linejoin:round;pointer-events:none"><path d="M6 9l6 6 6-6"/></svg></div>
      '''
rep('<label id="wl" data-i18n="who">Who did the duty</label>', SEL + '<label id="wl" data-i18n="who">Who did the duty</label>')
ESEL = SEL.replace('hsl', 'ehsl').replace('id="hsel"', 'id="ehsel"')
rep('<label id="ewl" data-i18n="who">Who did the duty</label>', ESEL + '<label id="ewl" data-i18n="who">Who did the duty</label>')

# Head dialog (add / update name)
HMODAL = '''
<div id="hmodal" class="overlay" hidden role="dialog" aria-modal="true" aria-labelledby="hmt">
  <div class="dialog">
    <h2 id="hmt" data-i18n="hm_edit_t">Update name</h2>
    <label for="hmnew" style="margin-top:0" data-i18n="hm_title">Head Of Manager</label>
    <input type="text" id="hmnew" maxlength="40" autocomplete="off">
    <p class="msg err" id="hmerr" aria-live="polite"></p>
    <div class="dactions">
      <button class="btn ghost" id="hmcancel" type="button" data-i18n="cancel">Cancel</button>
      <button class="btn" id="hmok" type="button" data-i18n="update">Update</button>
    </div>
  </div>
</div>
'''
rep('<div id="emodal" class="overlay"', HMODAL + '<div id="emodal" class="overlay"')

# ---------- My Total Bill: head box ----------
rep('<div id="dbody" hidden><div id="dout"></div></div>',
    '<div id="dbody" hidden><div id="hbbox" style="margin:2px 0 12px"><label for="hbin" style="display:block;margin-top:0" data-i18n="hm_sel">Select Head Of Manager</label><input type="text" id="hbin" data-i18n-ph="hm_sel_ph" placeholder="Example - Shelar sir" autocomplete="off"><div id="hbsug"></div></div><div id="dout"></div></div>')

# ---------- Add Duty: compulsory, saved ----------
rep('var ok = $("date").value && $("loc").value.trim() && document.querySelectorAll("#who input:checked").length > 0;',
    'var ok = $("date").value && $("loc").value.trim() && $("hsel").value.trim() && document.querySelectorAll("#who input:checked").length > 0;')
rep('    if (!ids.length) return say($("msg"), tx("select_emp"), true);',
    '    if (!ids.length) return say($("msg"), tx("select_emp"), true);\n    if (!$("hsel").value.trim()) return say($("msg"), tx("hm_sel"), true);')
rep('state.records.push({ id: newId, date: date, loc: loc, duty: duty, names: names });',
    'state.records.push({ id: newId, date: date, loc: loc, duty: duty, names: names, head: $("hsel").value.trim() });')
# edit
rep('$("edate").value = r.date; $("eloc").value = r.loc; $("emsg").textContent = "";',
    '$("edate").value = r.date; $("eloc").value = r.loc; $("emsg").textContent = ""; $("ehsel").value = r.head || "";')
rep('    if (!names.length) return say($("emsg"), tx("select_emp"), true);',
    '    if (!names.length) return say($("emsg"), tx("select_emp"), true);\n    if (!$("ehsel").value.trim()) return say($("emsg"), tx("hm_sel"), true);')
rep('r.date = date; r.loc = loc; r.duty = dt ? dt.value : r.duty; r.names = names;',
    'r.date = date; r.loc = loc; r.duty = dt ? dt.value : r.duty; r.names = names; r.head = $("ehsel").value.trim();')
# saved table
rep("""return '<tr data-rid="' + r.id + '"><td><b>' + esc(fmt(r.date)) + '</b></td>""",
    """return '<tr data-rid="' + r.id + '"><td><b>' + esc(fmt(r.date)) + '</b>' + (r.head ? '<div class="hmtag">' + esc(r.head) + '</div>' : '') + '</td>""")
rep("</style>\n", "</style>\n<style>/* BK-HEADS */.hmtag{margin-top:4px;font-size:11px;font-weight:600;color:#4338ca;line-height:1.2;word-break:break-word}</style>\n", n=f.count("</style>\n") and 1) if False else None
f = f.replace("</head>", "<style>/* BK-HEADS */.hmtag{margin-top:4px;font-size:11px;font-weight:600;color:#4338ca;line-height:1.2;word-break:break-word}#hbsug .hbs{background:#fff;border-radius:16px;margin-top:6px;box-shadow:0 8px 24px rgba(40,30,120,.25);overflow:hidden}#hbsug .hbi{display:flex;align-items:center;gap:10px;padding:11px 14px;font-weight:600;color:#1b1b2f;cursor:pointer;border-top:1px solid #eee}#hbsug .hbi:first-child{border-top:0}#hbsug .hbi i{width:30px;height:30px;border-radius:50%;background:linear-gradient(135deg,#4338ca,#6d28d9);color:#fff;display:flex;align-items:center;justify-content:center;font-size:13px;font-style:normal;flex:none}</style></head>", 1)

# ---------- My Total Bill: only the chosen head's duties ----------
rep('''    var groups = {}, order = [], fd = 0, hd = 0;
    state.records.forEach(function (r) {''', '''    var groups = {}, order = [], fd = 0, hd = 0;
    headRecs().forEach(function (r) {''')
rep("""    if (!order.length) { out.innerHTML = '<p class="hint">' + esc(tx("no_duties")) + '</p>'; return; }""",
    """    if (!order.length) { out.innerHTML = '<p class="hint">' + esc(tx(curHead ? "no_duties" : "hm_pick")) + '</p>'; return; }""")
rep('''  function completeBill() {
    var total = 0;
    state.records.forEach(function (r) {''', '''  function completeBill() {
    var total = 0;
    headRecs().forEach(function (r) {''')
rep('''    var hAmt = 0, fAmt = 0, hr = {}, fr = {};
    state.records.forEach(function (r) {''', '''    var hAmt = 0, fAmt = 0, hr = {}, fr = {};
    if (!curHead) return;
    headRecs().forEach(function (r) {''')
rep('{ title: title, fname: title.replace(/[\\\\\\/:*?"<>|]+/g, "").trim() + ".pdf", box: "dacts" }',
    '{ title: title, fname: title.replace(/[\\\\\\/:*?"<>|]+/g, "").trim() + ".pdf", box: "dacts", head: curHead }')
# PDF corner
rep('''    } else { doc.text(nameText, W / 2, 17, { align: "center" }); }
    var h1 = cellHooks(''', '''    } else { doc.text(nameText, W / 2, 17, { align: "center" }); }
    if (my && my.head) {
      var hc = "Head Of Manager: " + my.head;
      if (pdfUni(hc)) { var hi = pdfTextImg(hc, 90, 9, "#ffeaa0", true, "#4338ca", true); doc.addImage(hi.data, "PNG", W - 12 - hi.w, 8 - hi.h / 2, hi.w, hi.h); }
      else { doc.setFont("helvetica", "bold"); doc.setFontSize(9); doc.setTextColor(255, 234, 160); doc.text(hc, W - 12, 8, { align: "right" }); doc.setTextColor(255, 255, 255); doc.setFontSize(18); }
    }
    var h1 = cellHooks(''')

# ---------- Trash ----------
rep('row.querySelector(".tmeta").textContent = txc("duty", t.records.length) + " · " + txc("adv", t.advances.length) + " · " + tx("deleted_on", { date: fmt(t.deletedAt) });',
    'row.querySelector(".tmeta").textContent = t.kind === "head" ? tx("hm_title") + " · " + tx("deleted_on", { date: fmt(t.deletedAt) }) : txc("duty", t.records.length) + " · " + txc("adv", t.advances.length) + " · " + tx("deleted_on", { date: fmt(t.deletedAt) });')
rep("  function restoreTrash(t) {\n", "  function restoreTrash(t) {\n    if (t.kind === \"head\") return restoreHead(t);\n")

# ---------- Backup ----------
rep("data: { employees: state.employees, records: state.records, advances: state.advances, trash: state.trash, rates: state.rates }",
    "data: { employees: state.employees, records: state.records, advances: state.advances, trash: state.trash, rates: state.rates, heads: state.heads }")
rep("var out = { employees: [], records: [], advances: [], trash: [], pending: {} };", "var out = { employees: [], records: [], advances: [], trash: [], pending: {}, heads: [] };\n    (Array.isArray(d.heads) ? d.heads : []).forEach(function (h) { if (h && typeof h.name === \"string\" && h.name.trim()) out.heads.push({ id: h.id !== undefined && h.id !== null ? h.id : uid(), name: h.name.trim() }); });")
rep('out.records.push({ id: r.id !== undefined && r.id !== null ? r.id : uid(), date: r.date, loc: typeof r.loc === "string" ? r.loc : "", duty: r.duty, names: r.names.slice() });',
    'var nr = { id: r.id !== undefined && r.id !== null ? r.id : uid(), date: r.date, loc: typeof r.loc === "string" ? r.loc : "", duty: r.duty, names: r.names.slice() }; if (typeof r.head === "string" && r.head) nr.head = r.head; out.records.push(nr);')
rep("if (t.rates && typeof t.rates === \"object\") nt.rates = t.rates;", "if (t.rates && typeof t.rates === \"object\") nt.rates = t.rates;\n      if (t.kind === \"head\") nt.kind = \"head\";")
rep("renderRates(); renderWho(); renderLocs(); renderEmps(); renderList(); renderTrash(); renderAdv();", "renderRates(); renderWho(); renderLocs(); renderEmps(); renderHeads(); renderList(); renderTrash(); renderAdv();")

# ---------- JS ----------
JS = r'''
  /* BK-HEADS: Head Of Manager */
  var curHead = "";
  function headNames() { return state.heads.map(function (h) { return h.name; }); }
  function headRecs() { return curHead ? state.records.filter(function (r) { return r.head === curHead; }) : []; }
  function headMatch(v) {
    v = String(v || "").trim().toLowerCase(); if (!v) return "";
    var hit = headNames().filter(function (n) { return n.toLowerCase() === v; })[0];
    return hit || "";
  }
  var headIc = { edit: '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M12 20h9"/><path d="M16.5 3.5a2.1 2.1 0 0 1 3 3L7 19l-4 1 1-4Z"/></svg>',
    del: '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M3 6h18"/><path d="M8 6V4h8v2"/><path d="M19 6l-1 14H6L5 6"/><path d="M10 11v6M14 11v6"/></svg>' };
  function syncHeadPickers() {
    var names = headNames();
    ["hsel", "ehsel"].forEach(function (id) { if ($(id) && $(id).value && names.indexOf($(id).value) < 0 && id === "hsel") $(id).value = ""; });
    if ($("hbin")) { var m = headMatch($("hbin").value); if (!m) { $("hbin").value = $("hbin").value; } curHead = m; }
    updateSave(); renderDetails();
  }
  function renderHeads() {
    var box = $("hmlist"); if (!box) return; box.innerHTML = "";
    state.heads.forEach(function (h) {
      var row = document.createElement("div"); row.className = "row erow"; row.setAttribute("data-id", h.id);
      row.innerHTML = '<span class="avatar" aria-hidden="true"></span><span class="ename"></span>' +
        '<button class="ibtn" type="button" title="' + esc(tx("hm_edit_t")) + '" aria-label="' + esc(tx("hm_edit_t")) + '">' + headIc.edit + '</button>' +
        '<button class="ibtn del" type="button" title="' + esc(tx("hm_del_t")) + '" aria-label="' + esc(tx("hm_del_t")) + '">' + headIc.del + '</button>';
      row.querySelector(".avatar").textContent = (graphemes(h.name)[0] || "?").toUpperCase();
      row.querySelector(".ename").textContent = h.name;
      var bs = row.querySelectorAll("button");
      bs[0].onclick = function () { openHeadEdit(h); };
      bs[1].onclick = function () { deleteHead(h); };
      box.appendChild(row);
    });
    syncHeadPickers();
  }
  function headDup(n, skipId) {
    var k = n.toLowerCase();
    return state.heads.some(function (h) { return h.id !== skipId && h.name.toLowerCase() === k; });
  }
  $("hmname").addEventListener("input", function () { $("hmadd").disabled = !this.value.trim(); });
  $("hmadd").onclick = function () {
    var n = $("hmname").value.trim(); if (!n) { $("hmadd").disabled = true; return; }
    if (headDup(n)) return say($("hmmsg"), tx("hm_exists"), true);
    state.heads.push({ id: uid(), name: n });
    persist(); $("hmname").value = ""; $("hmadd").disabled = true; say($("hmmsg"), tx("saved"));
    renderHeads();
  };
  $("hmname").addEventListener("keydown", function (e) { if (e.key === "Enter") { e.preventDefault(); $("hmadd").click(); } });
  function deleteHead(h) {
    state.heads = state.heads.filter(function (x) { return x.id !== h.id; });
    state.trash.push({ id: uid(), kind: "head", name: h.name, empId: null, deletedAt: today(), records: [], advances: [] });
    persist(); renderHeads(); renderTrash();
  }
  function restoreHead(t) {
    if (headDup(t.name)) return say($("tmsg"), tx("hm_exists"), true);
    state.heads.push({ id: uid(), name: t.name });
    state.trash = state.trash.filter(function (x) { return x.id !== t.id; });
    persist(); say($("tmsg"), tx("restored", { name: t.name })); renderHeads(); renderTrash();
  }
  var headEditId = null;
  function openHeadEdit(h) { headEditId = h.id; $("hmnew").value = h.name; $("hmerr").textContent = ""; $("hmodal").hidden = false; $("hmnew").focus(); $("hmnew").select(); }
  function closeHeadEdit() { $("hmodal").hidden = true; headEditId = null; }
  $("hmcancel").onclick = closeHeadEdit;
  $("hmok").onclick = function () {
    var h = state.heads.filter(function (x) { return x.id === headEditId; })[0]; if (!h) return closeHeadEdit();
    var n = $("hmnew").value.trim(), old = h.name;
    if (!n) return say($("hmerr"), tx("name_empty"), true);
    if (n === old) return closeHeadEdit();
    if (headDup(n, h.id)) return say($("hmerr"), tx("hm_exists"), true);
    h.name = n;
    state.records.forEach(function (r) { if (r.head === old) r.head = n; });
    if ($("hsel").value === old) $("hsel").value = n;
    if ($("hbin").value.trim().toLowerCase() === old.toLowerCase()) $("hbin").value = n;
    persist(); closeHeadEdit(); renderHeads(); renderList();
  };
  // popup list of heads (Add Duty and Update duty)
  function openHeadPicker(current, cb) {
    var ov = document.createElement("div");
    ov.style.cssText = "position:fixed;inset:0;z-index:99999;background:rgba(5,6,10,.72);display:flex;align-items:flex-end;justify-content:center";
    var sheet = document.createElement("div");
    sheet.style.cssText = "width:100%;max-width:430px;max-height:80vh;overflow:auto;background:#e3dcfb;border:4px solid #fff;border-bottom:0;border-radius:26px 26px 0 0;padding:18px 16px 22px;box-shadow:0 -12px 40px rgba(0,0,0,.5);box-sizing:border-box";
    var h3 = document.createElement("h3"); h3.style.cssText = "margin:0 0 12px;font-size:18px;color:#1b1b2f"; h3.textContent = tx("hm_sel"); sheet.appendChild(h3);
    var close = function () { if (ov.parentNode) ov.parentNode.removeChild(ov); };
    if (!state.heads.length) {
      var p = document.createElement("p"); p.style.cssText = "margin:0 0 12px;color:#1b1b2f;font-weight:600"; p.textContent = tx("hm_none"); sheet.appendChild(p);
    }
    state.heads.forEach(function (h) {
      var on = h.name === current;
      var it = document.createElement("div");
      it.style.cssText = "display:flex;align-items:center;gap:12px;padding:12px 14px;margin-bottom:8px;border-radius:16px;font-weight:600;cursor:pointer;" + (on ? "background:linear-gradient(90deg,#4338ca,#6d28d9);color:#fff" : "background:#fff;color:#1b1b2f");
      it.innerHTML = '<span style="width:38px;height:38px;border-radius:50%;display:flex;align-items:center;justify-content:center;color:#fff;flex:none;background:' + (on ? "rgba(255,255,255,.25)" : "linear-gradient(135deg,#4338ca,#6d28d9)") + '"></span><span style="flex:1;font-size:16px;word-break:break-word"></span>' + (on ? '<span style="font-size:18px">✓</span>' : "");
      it.children[0].textContent = (graphemes(h.name)[0] || "?").toUpperCase(); it.children[1].textContent = h.name;
      it.onclick = function () { close(); cb(h.name); };
      sheet.appendChild(it);
    });
    var cn = document.createElement("button"); cn.type = "button"; cn.textContent = tx("cancel");
    cn.style.cssText = "width:100%;margin-top:6px;padding:13px;border:1.5px solid #4338ca;border-radius:16px;background:transparent;color:#4338ca;font-weight:700;font-size:15px;font-family:inherit;cursor:pointer";
    cn.onclick = close; sheet.appendChild(cn);
    ov.appendChild(sheet); ov.addEventListener("click", function (e) { if (e.target === ov) close(); });
    document.body.appendChild(ov);
  }
  $("hsel").addEventListener("click", function () { openHeadPicker($("hsel").value, function (n) { $("hsel").value = n; updateSave(); }); });
  $("ehsel").addEventListener("click", function () { openHeadPicker($("ehsel").value, function (n) { $("ehsel").value = n; }); });
  // My Total Bill: type to find a head, the list shows by itself
  function showHeadSug() {
    var v = $("hbin").value.trim().toLowerCase(), box = $("hbsug");
    var list = state.heads.filter(function (h) { return !v || h.name.toLowerCase().indexOf(v) >= 0; });
    var cm = headMatch($("hbin").value);
    if (cm && list.length === 1 && list[0].name === cm) list = [];
    if (!list.length) { box.innerHTML = ""; return; }
    box.innerHTML = '<div class="hbs">' + list.map(function (h, i) { return '<div class="hbi" data-i="' + i + '"><i></i><span></span></div>'; }).join("") + "</div>";
    [].forEach.call(box.querySelectorAll(".hbi"), function (el, i) {
      el.children[0].textContent = (graphemes(list[i].name)[0] || "?").toUpperCase(); el.children[1].textContent = list[i].name;
      el.onmousedown = el.ontouchstart = function (e) { e.preventDefault(); };
      el.onclick = function () { $("hbin").value = list[i].name; box.innerHTML = ""; curHead = list[i].name; renderDetails(); };
    });
  }
  $("hbin").addEventListener("input", function () { curHead = headMatch(this.value); showHeadSug(); renderDetails(); });
  $("hbin").addEventListener("focus", showHeadSug);
  $("hbin").addEventListener("blur", function () { setTimeout(function () { $("hbsug").innerHTML = ""; }, 200); });
'''
rep("  function refreshAll() {", JS + "  function refreshAll() {")
# first paint
rep("  renderWho(); renderLocs(); renderEmps(); renderList(); renderTrash();", "  renderWho(); renderLocs(); renderEmps(); renderHeads(); renderList(); renderTrash();")

# ---------- translations ----------
T = {
 "en": ["Head Of Manager", "Add Head Of Manager", "Ex. Shelar sir", "Select Head Of Manager", "Example - Shelar sir", "No heads yet. Add names in Settings first.", "Select a Head Of Manager to see his duties.", "This head is already in the list.", "Update name", "Delete (moves to Trash)"],
 "hi": ["हेड ऑफ मैनेजर", "हेड ऑफ मैनेजर जोड़ें", "उदा. शेलार सर", "हेड ऑफ मैनेजर चुनें", "उदाहरण - शेलार सर", "अभी कोई हेड नहीं है। पहले सेटिंग्स में नाम जोड़ें।", "उसके ड्यूटी देखने के लिए हेड ऑफ मैनेजर चुनें।", "यह हेड पहले से सूची में है।", "नाम अपडेट करें", "हटाएं (ट्रैश में जाएगा)"],
 "mr": ["हेड ऑफ मॅनेजर", "हेड ऑफ मॅनेजर जोडा", "उदा. शेलार सर", "हेड ऑफ मॅनेजर निवडा", "उदाहरण - शेलार सर", "अजून कोणीही हेड नाही. आधी सेटिंग्जमध्ये नावे जोडा.", "त्यांच्या ड्युटी पाहण्यासाठी हेड ऑफ मॅनेजर निवडा.", "हे हेड आधीच यादीत आहे.", "नाव अपडेट करा", "हटवा (ट्रॅशमध्ये जाईल)"],
 "gu": ["હેડ ઓફ મેનેજર", "હેડ ઓફ મેનેજર ઉમેરો", "દા.ત. શેલાર સર", "હેડ ઓફ મેનેજર પસંદ કરો", "ઉદાહરણ - શેલાર સર", "હજુ કોઈ હેડ નથી. પહેલા સેટિંગ્સમાં નામ ઉમેરો.", "તેમની ડ્યુટી જોવા હેડ ઓફ મેનેજર પસંદ કરો.", "આ હેડ પહેલેથી યાદીમાં છે.", "નામ અપડેટ કરો", "કાઢી નાખો (ટ્રેશમાં જશે)"],
 "pa": ["ਹੈੱਡ ਆਫ ਮੈਨੇਜਰ", "ਹੈੱਡ ਆਫ ਮੈਨੇਜਰ ਜੋੜੋ", "ਜਿਵੇਂ ਸ਼ੇਲਾਰ ਸਰ", "ਹੈੱਡ ਆਫ ਮੈਨੇਜਰ ਚੁਣੋ", "ਉਦਾਹਰਣ - ਸ਼ੇਲਾਰ ਸਰ", "ਅਜੇ ਕੋਈ ਹੈੱਡ ਨਹੀਂ। ਪਹਿਲਾਂ ਸੈਟਿੰਗਜ਼ ਵਿੱਚ ਨਾਮ ਜੋੜੋ।", "ਉਹਨਾਂ ਦੀਆਂ ਡਿਊਟੀਆਂ ਦੇਖਣ ਲਈ ਹੈੱਡ ਆਫ ਮੈਨੇਜਰ ਚੁਣੋ।", "ਇਹ ਹੈੱਡ ਪਹਿਲਾਂ ਹੀ ਸੂਚੀ ਵਿੱਚ ਹੈ।", "ਨਾਮ ਅੱਪਡੇਟ ਕਰੋ", "ਮਿਟਾਓ (ਟ੍ਰੈਸ਼ ਵਿੱਚ ਜਾਵੇਗਾ)"],
 "ta": ["ஹெட் ஆஃப் மேனேஜர்", "ஹெட் ஆஃப் மேனேஜரை சேர்", "எ.கா. ஷேலார் சார்", "ஹெட் ஆஃப் மேனேஜரைத் தேர்ந்தெடுக்கவும்", "உதாரணம் - ஷேலார் சார்", "இன்னும் ஹெட் இல்லை. முதலில் அமைப்புகளில் பெயர்களைச் சேர்க்கவும்.", "அவரது பணிகளைக் காண ஹெட் ஆஃப் மேனேஜரைத் தேர்ந்தெடுக்கவும்.", "இந்த ஹெட் ஏற்கனவே பட்டியலில் உள்ளார்.", "பெயரைப் புதுப்பி", "நீக்கு (குப்பையில் சேரும்)"],
 "te": ["హెడ్ ఆఫ్ మేనేజర్", "హెడ్ ఆఫ్ మేనేజర్‌ను జోడించండి", "ఉదా. శేలార్ సర్", "హెడ్ ఆఫ్ మేనేజర్‌ను ఎంచుకోండి", "ఉదాహరణ - శేలార్ సర్", "ఇంకా హెడ్ లేరు. ముందుగా సెట్టింగ్స్‌లో పేర్లు జోడించండి.", "అతని డ్యూటీలు చూడటానికి హెడ్ ఆఫ్ మేనేజర్‌ను ఎంచుకోండి.", "ఈ హెడ్ ఇప్పటికే జాబితాలో ఉన్నారు.", "పేరు అప్‌డేట్ చేయండి", "తొలగించు (ట్రాష్‌కు వెళ్తుంది)"],
 "kn": ["ಹೆಡ್ ಆಫ್ ಮ್ಯಾನೇಜರ್", "ಹೆಡ್ ಆಫ್ ಮ್ಯಾನೇಜರ್ ಸೇರಿಸಿ", "ಉದಾ. ಶೇಲಾರ್ ಸರ್", "ಹೆಡ್ ಆಫ್ ಮ್ಯಾನೇಜರ್ ಆಯ್ಕೆಮಾಡಿ", "ಉದಾಹರಣೆ - ಶೇಲಾರ್ ಸರ್", "ಇನ್ನೂ ಹೆಡ್ ಇಲ್ಲ. ಮೊದಲು ಸೆಟ್ಟಿಂಗ್ಸ್‌ನಲ್ಲಿ ಹೆಸರುಗಳನ್ನು ಸೇರಿಸಿ.", "ಅವರ ಡ್ಯೂಟಿಗಳನ್ನು ನೋಡಲು ಹೆಡ್ ಆಫ್ ಮ್ಯಾನೇಜರ್ ಆಯ್ಕೆಮಾಡಿ.", "ಈ ಹೆಡ್ ಈಗಾಗಲೇ ಪಟ್ಟಿಯಲ್ಲಿದ್ದಾರೆ.", "ಹೆಸರು ಅಪ್‌ಡೇಟ್ ಮಾಡಿ", "ಅಳಿಸಿ (ಟ್ರ್ಯಾಶ್‌ಗೆ ಹೋಗುತ್ತದೆ)"]}
KEYS = ["hm_title", "hm_label", "hm_ph", "hm_sel", "hm_sel_ph", "hm_none", "hm_pick", "hm_exists", "hm_edit_t", "hm_del_t"]
for lg, vals in T.items():
    m = re.search(r'(\n?\s*(?:var I18N = \{ )?%s: \{)(")' % lg, f)
    assert m, lg
    d = dict(zip(KEYS, vals)); d["hm_add"] = vals[1]
    ins = "".join('%s: %s, ' % (json.dumps(k), json.dumps(v, ensure_ascii=False)) for k, v in d.items())
    f = f[:m.end(1)] + ins + f[m.end(1):]
open(fp, "w", encoding="utf-8").write(f)
print("heads: patched")

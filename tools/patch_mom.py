#!/usr/bin/env python3
"""App-only: builds "Manager of Managers" (assets/www/mom) from the already patched Duty Manager page and adds its front-page card.
Each saved duty is one manager + a labourer count (cnt); bills multiply the manager's rate by the count. Compare PDF is hidden for now.
Usage: patch_mom.py <assets/www folder>   (idempotent: rebuilt every run)"""
import os, sys
root = sys.argv[1]
src = os.path.join(root, "forall", "index.html")
s = open(src, encoding="utf-8").read()

def rep(a, b, n=1):
    global s
    c = s.count(a)
    assert c == n, (c, n, a[:80])
    s = s.replace(a, b)

# separate storage
rep('var KEY = "dutylog.v1";', 'var KEY = "momlog.v1";')
rep('var LANG_KEY = "dutylog.lang"', 'var LANG_KEY = "momlog.lang"')
rep('<title>BillKarta</title>', '<title>Manager of Managers</title>')
rep('kind: "duty-backup"', 'kind: "manager-backup"')
# labourer-count helper
rep('  var mem = null;\n', '  var mem = null;\n  function cntOf(r) { var c = Number(r && r.cnt); return c > 0 ? Math.floor(c) : 1; }\n')
# no per-day limits: a manager can have many labourers on any day
for fn in ("halfLimit", "comboLimit", "fullConflict"):
    sig = "function %s(date, duty, names, skipId) {" % fn
    rep(sig, sig + ' return "";')
# totals, tables and bill use the labourer count
rep('counts[n][r.duty]++;', 'counts[n][r.duty] += cntOf(r);')
rep('(r.duty === "Full" ? tx("fd") : tx("hd")) + \'</span></td>\'', '(r.duty === "Full" ? tx("fd") : tx("hd")) + " \\u00d7" + cntOf(r) + \'</span></td>\'')
rep('total += rateOf(e, r.duty);', 'total += rateOf(e, r.duty) * cntOf(r);')
rep('var n = r.names.length;', 'var n = r.names.length * cntOf(r);')
rep('var amt = rateOf(emp0, r.duty);', 'var amt = rateOf(emp0, r.duty) * cntOf(r);')
rep('total += amt; if (r.duty === "Full") fd++; else hd++;', 'total += amt; if (r.duty === "Full") fd += cntOf(r); else hd += cntOf(r);')
c1 = s.count('r.duty === "Half" ? "1" : ""'); c2 = s.count('r.duty === "Full" ? "1" : ""')
assert c1 >= 2 and c2 >= 2, (c1, c2)
s = s.replace('r.duty === "Half" ? "1" : ""', 'r.duty === "Half" ? String(cntOf(r)) : ""').replace('r.duty === "Full" ? "1" : ""', 'r.duty === "Full" ? String(cntOf(r)) : ""')
# trash + restore + backup keep the count
rep('return { id: r.id, date: r.date, loc: r.loc, duty: r.duty }; });', 'return { id: r.id, date: r.date, loc: r.loc, duty: r.duty, cnt: cntOf(r) }; });')
rep('duty: tr.duty, names: [t.name] });', 'duty: tr.duty, names: [t.name], cnt: cntOf(tr) });')
rep('duty: r.duty, names: r.names.slice() });', 'duty: r.duty, names: r.names.slice(), cnt: cntOf(r) });')
# saved duties: date and location shown once per day+place (merged cells), one line per manager
rep('$("list").innerHTML = recs.length', 'var sp = momSpans(recs);\n    $("list").innerHTML = recs.length')
rep("""return '<tr data-rid="' + r.id + '"><td><b>' + esc(fmt(r.date)) + '</b></td><td>' + esc(r.loc) + '</td>' +""",
    """return '<tr data-rid="' + r.id + '">' + (sp[r.id] ? '<td class="g" rowspan="' + sp[r.id] + '"><b>' + esc(fmt(r.date)) + '</b></td><td class="g" rowspan="' + sp[r.id] + '">' + esc(r.loc) + '</td>' : '') +""")
rep("""'<td><ol class="names">' + r.names.map(function (n) { return "<li>" + esc(n) + "</li>"; }).join("") + '</ol></td>' +""", """'<td class="mnm">' + r.names.map(esc).join(", ") + '</td>' +""")
rep('  function renderList() {', """  function momHighlight(ids) {
    var rows = ids.map(function (id) { return document.querySelector('tr[data-rid="' + id + '"]'); }).filter(Boolean);
    if (!rows.length) return;
    var calm = window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    var mid = rows[Math.floor(rows.length / 2)];
    mid.scrollIntoView({ behavior: calm ? "auto" : "smooth", block: "center" });
    var cells = [];
    rows.forEach(function (row) {
      row.classList.add("hl");
      var g = row;
      while (g && !g.querySelector("td.g")) g = g.previousElementSibling;
      if (g) [].forEach.call(g.querySelectorAll("td.g"), function (c) { c.classList.add("hlg"); cells.push(c); });
    });
    setTimeout(function () { rows.forEach(function (row) { row.classList.remove("hl"); }); cells.forEach(function (c) { c.classList.remove("hlg"); }); }, 2400);
  }
  function momSpans(recs) {
    var sp = {}, first = null, key = null, n = 0;
    recs.forEach(function (r) {
      var k = r.date + "|" + String(r.loc).trim().toLowerCase();
      if (k !== key) { if (first) sp[first] = n; key = k; first = r.id; n = 0; }
      n++;
    });
    if (first) sp[first] = n;
    return sp;
  }
  function renderList() {""")
# duty form: manager rows with - / number / +
i = s.index("  function renderWho() {"); j = s.index("  function renderLocs() {")
s = s[:i] + '''  function mgrTotal() {
    var t = 0;
    [].forEach.call(document.querySelectorAll("#who input[data-emp]"), function (x) { var n = Math.floor(Number(x.value)); if (n > 0) t += n; });
    return t;
  }
  function mgrSum() {
    var e = $("mtot"); if (e) e.textContent = String(mgrTotal());
    [].forEach.call(document.querySelectorAll("#who .mrow"), function (r) { var i = r.querySelector("input"); r.classList.toggle("z", !(Math.floor(Number(i.value)) > 0)); });
  }
  function mgrFocus(row) {
    [].forEach.call(document.querySelectorAll("#who .mrow.on"), function (r) { if (r !== row) r.classList.remove("on"); });
    if (row) row.classList.add("on");
  }
  function renderWho() {
    var box = $("who"); box.innerHTML = ""; box.className = "mgr";
    $("nowho").hidden = state.employees.length > 0;
    state.employees.forEach(function (e) {
      var d = document.createElement("div"); d.className = "mrow";
      d.innerHTML = '<span class="mn">' + esc(e.name) + '</span><span class="mst"><button type="button" class="mb" data-d="-1" aria-label="-">\\u2212</button>' +
        '<input type="number" class="mc" data-emp="' + e.id + '" min="0" max="9999" step="1" inputmode="numeric" value="0" aria-label="' + esc(e.name) + '">' +
        '<button type="button" class="mb" data-d="1" aria-label="+">+</button></span>';
      box.appendChild(d);
    });
    if (state.employees.length) {
      var t = document.createElement("div"); t.className = "mtot"; t.innerHTML = '<span>Total Employees</span><b id="mtot" class="mcount">0</b>';
      box.appendChild(t);
    }
    mgrSum(); updateSave();
  }
''' + s[j:]
rep('document.querySelectorAll("#who input:checked").length > 0;', 'mgrTotal() > 0;')
rep('$("who").addEventListener("change", updateSave);', '''$("who").addEventListener("change", function () { mgrSum(); updateSave(); });
  $("who").addEventListener("input", function () { mgrFocus(document.activeElement && document.activeElement.closest ? document.activeElement.closest(".mrow") : null); mgrSum(); updateSave(); });
  $("who").addEventListener("click", function (ev) {
    var b = ev.target.closest ? ev.target.closest(".mb") : null; if (!b) return;
    var inp = b.parentNode.querySelector("input"), v = Math.floor(Number(inp.value)) || 0;
    v = Math.max(0, Math.min(9999, v + Number(b.getAttribute("data-d")))); inp.value = String(v); mgrFocus(b.closest(".mrow")); mgrSum(); updateSave();
  });''')
i = s.index('  $("save").onclick = function () {'); j = s.index("  // Records\n", i)
s = s[:i] + '''  $("save").onclick = function () {
    var date = $("date").value, loc = $("loc").value.trim();
    var duty = document.querySelector('input[name="duty"]:checked').value;
    var items = [];
    [].forEach.call(document.querySelectorAll("#who input[data-emp]"), function (x) {
      var n = Math.floor(Number(x.value)); if (!(n > 0)) return;
      var e = state.employees.filter(function (q) { return q.id === x.getAttribute("data-emp"); })[0];
      if (e) items.push({ name: e.name, cnt: n });
    });
    if (!date) return say($("msg"), tx("choose_date"), true);
    if (!loc) return say($("msg"), tx("enter_location"), true);
    if (!items.length) return say($("msg"), tx("select_emp"), true);
    var newIds = [];
    items.forEach(function (it) {
      var key = String(loc).trim().toLowerCase();
      var same = state.records.filter(function (x) {
        return x.date === date && x.duty === duty && String(x.loc).trim().toLowerCase() === key && x.names.length === 1 && x.names[0] === it.name;
      })[0];
      if (same) { same.cnt = Math.min(9999, cntOf(same) + it.cnt); newIds.push(same.id); return; }
      var lastId = uid(); newIds.push(lastId);
      state.records.push({ id: lastId, date: date, loc: loc, duty: duty, names: [it.name], cnt: it.cnt });
    });
    var ok = persist();
    [].forEach.call(document.querySelectorAll("#who input[data-emp]"), function (x) { x.value = "0"; });
    mgrSum(); updateSave();
    say($("msg"), ok ? tx("saved") : tx("saved_blocked"), !ok);
    renderLocs(); renderList();
    momHighlight(newIds);
  };

''' + s[j:]
# edit dialog: labourer count
rep('<label id="ewl" data-i18n="who">Who did the duty</label>', '<label id="ewl" data-i18n="mgr_one">Manager</label>')
rep('<div class="chips" id="ewho" role="group" aria-labelledby="ewl"></div>',
    '<div class="chips" id="ewho" role="group" aria-labelledby="ewl"></div>\n    <label for="ecnt">No. Of Employees</label>\n    <div class="estep"><button type="button" class="mb" id="ecm" aria-label="-">−</button><input type="number" id="ecnt" class="mc" min="1" max="9999" step="1" inputmode="numeric"><button type="button" class="mb" id="ecp" aria-label="+">+</button></div>')
# edit: the manager of this entry is fixed; only the count (and date, location, duty type) can change
i = s.index('    var names = state.employees.map(function (e) { return e.name; });\n    r.names.forEach') if False else None
_a = s.index('    var names = state.employees.map(function (e) { return e.name; });\n    r.names.forEach')
_b = s.index('    $("emodal").hidden = false; $("edate").focus();', _a)
s = s[:_a] + """    var box = $("ewho");
    box.innerHTML = '<div class="mfix"></div>';
    box.firstChild.textContent = r.names.join(", ");
    $("ecnt").value = String(cntOf(r));
""" + s[_b:]
rep('$("emodal").hidden = false; $("edate").focus();', '$("emodal").hidden = false; $("edate").focus();')
rep('var names = [].slice.call(document.querySelectorAll("#ewho input:checked")).map(function (c) { return c.value; });',
    'var names = (state.records.filter(function (x) { return x.id === editId; })[0] || { names: [] }).names.slice();')
rep('$("ecancel").onclick = closeEdit;', """$("ecancel").onclick = closeEdit;
  function ecStep(d) { var v = Math.floor(Number($("ecnt").value)) || 1; $("ecnt").value = String(Math.max(1, Math.min(9999, v + d))); }
  $("ecm").onclick = function () { ecStep(-1); };
  $("ecp").onclick = function () { ecStep(1); };""")
rep('r.duty = dt ? dt.value : r.duty; r.names = names;', 'r.duty = dt ? dt.value : r.duty; r.names = names; r.cnt = Math.max(1, Math.min(9999, Math.floor(Number($("ecnt").value)) || 1));')
# wording (English) and styles
rep('var LANG_KEY = "momlog.lang", lang = "en", memLang = null;', '''var LANG_KEY = "momlog.lang", lang = "en", memLang = null;
  Object.assign(I18N.en, { who: "No. Of Emp of Managers", mgr_one: "Manager", no_emp_first: "No managers yet. Add names in Settings first.", select_emp: "Enter labourers for at least one manager.",
    bill_search: "Enter Manager Name", employee_name: "Manager name", bname_ph: "Type manager name", employees: "Managers", employee: "Manager",
    new_name: "New manager name", add: "Add Manager Name", all_emps: "All managers", emp_working: "Managers", emp_details: "All managers details",
    hint_emps: "Renaming also updates the name on past duties. Deleting a manager moves him and all of his duties and advances to Trash below.",
    hint_trash: "Deleted managers go here with all of their duties and advances. Restore them any time, or delete them permanently.",
    no_emp: "No managers yet.", no_emp_adv: "No managers yet. Add names in Settings.", no_match: "No matching manager" });''')
rep('</head>', '''<style>
#cmp,#cmpsheet{display:none!important}
.mgr{display:block}
.mfix{padding:10px 14px;border-radius:14px;background:#eef0f5;color:#17233b;font-weight:800}
.estep{display:flex;align-items:center;gap:10px;margin-top:6px}.estep .mb{width:40px;height:40px;flex:none}.estep .mc{width:70px!important;height:42px!important;flex:none}.estep .mc:focus{border-color:#5b3ad6!important;box-shadow:0 0 0 4px rgba(91,58,214,.25);background:#f3efff;outline:0}
.duties td.g{vertical-align:middle;border-right:1px solid rgba(0,0,0,.08)}.duties td.g.hlg{background:transparent;animation:dutyflash .7s ease-in-out 3}.duties td.mnm{font-weight:600;white-space:nowrap}
.duties td:last-child,.duties th:last-child{padding-left:.1rem!important;padding-right:.1rem!important}.duties td:first-child,.duties th:first-child{padding-left:.3rem!important}
.duties .names{padding-left:.7rem!important}.duties td b{letter-spacing:-.2px}.duties .tag{font-size:.68rem!important}.duties .acts{flex-wrap:nowrap}.duties .tag{padding:.15rem .3rem}
.duties .ibtn{width:30px!important;height:30px!important}.duties .acts{gap:3px}.duties td{font-size:.78rem}.duties td b{font-size:.7rem}.duties th{font-size:.7rem}
.duties .names li{white-space:nowrap}
.duties .tag{font-size:.72rem;padding:.2rem .45rem;white-space:nowrap}
.duties td,.duties th{padding-left:.2rem;padding-right:.2rem}
.mrow{display:flex;align-items:center;justify-content:space-between;gap:10px;padding:4px 10px;margin:0 0 5px;border:2px solid transparent;border-radius:14px;background:#fff;box-shadow:0 2px 10px rgba(0,0,0,.08);color:#17233b;transition:.15s}
.mrow .mn{font-weight:700;font-size:.95rem;min-width:0;overflow-wrap:anywhere}
.mst{display:flex;align-items:center;gap:8px;flex:none}
.mb{width:32px;height:32px;border-radius:50%;border:0;background:#e3e7f1;color:#17233b;font-size:19px;font-weight:700;line-height:1;padding:0;cursor:pointer}
.mc{width:48px!important;height:32px;margin:0!important;padding:0 4px!important;text-align:center;font-weight:800;font-size:1rem;border:2px solid #1d6b4f!important;border-radius:10px;background:#fff;color:#17233b;-moz-appearance:textfield}
.mc::-webkit-outer-spin-button,.mc::-webkit-inner-spin-button{-webkit-appearance:none;margin:0}
.mrow.on .mc{border-color:#5b3ad6!important;box-shadow:0 0 0 4px rgba(91,58,214,.25);background:#f3efff}
.mrow.z .mn,.mrow.z .mc{opacity:.5}
.mtot{display:flex;align-items:center;justify-content:space-between;gap:10px;padding:6px 4px 0;color:#17233b;font-weight:700}
.mcount{min-width:30px;height:30px;padding:0 8px;border-radius:15px;background:linear-gradient(135deg,#c13cc0,#6a3ad6);color:#fff;display:inline-flex;align-items:center;justify-content:center;font-size:15px;box-shadow:0 3px 8px rgba(106,58,214,.4)}
</style>
</head>''')
rep('<span data-i18n="add_duty">Add Duty</span>', '<span data-i18n="add_duty">Add Duty</span>')
out = os.path.join(root, "mom"); os.makedirs(out, exist_ok=True)
open(os.path.join(out, "index.html"), "w", encoding="utf-8").write(s)
print("mom: page built")

# front-page card
fp = os.path.join(root, "frontpage", "index.html")
f = open(fp, encoding="utf-8").read()
if "BK-MOM-CARD" not in f:
    anchor = '''        </button>

    </div>

    <div class="selected" id="selected"'''
    assert f.count(anchor) == 1
    card = '''        </button>

        <button type="button" class="tab" aria-pressed="false" data-name="Manager of Managers" data-url="../mom/index.html"><!-- BK-MOM-CARD -->
            <div class="tab-icon" aria-hidden="true">👷</div>
            <div class="tab-info">
                <h3>Manager of Managers</h3>
                <p>Track labourers of every manager</p>
            </div>
            <div class="arrow" aria-hidden="true">›</div>
        </button>

    </div>

    <div class="selected" id="selected"'''
    f = f.replace(anchor, card, 1)
    open(fp, "w", encoding="utf-8").write(f)
    print("front page: Manager of Managers card added")

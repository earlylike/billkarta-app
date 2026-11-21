  /* BK-COMPARE-PDF: compare an employee's PDF with the records on this page */
  var cmpEmp = null, cmpBuf = null, cmpUrl = null;
  var CMP_LATIN1 = function (u8) { var s = "", i, n = u8.length; for (i = 0; i < n; i += 8192) s += String.fromCharCode.apply(null, u8.subarray(i, Math.min(n, i + 8192))); return s; };
  function cmpInflate(u8) {
    var ds = new DecompressionStream("deflate"), w = ds.writable.getWriter();
    w.write(u8); w.close();
    return new Response(ds.readable).arrayBuffer().then(function (b) { return new Uint8Array(b); });
  }
  function cmpStreams(u8) {
    var s = CMP_LATIN1(u8), pos = 0, jobs = [];
    for (;;) {
      var k = s.indexOf("stream", pos);
      if (k < 0) break;
      pos = k + 6;
      if (s.slice(k - 3, k) === "end" || !/>>\s*$/.test(s.slice(Math.max(0, k - 6), k))) continue;
      var o = s.lastIndexOf(" obj", k), dict = s.slice(o < 0 ? 0 : o, k);
      var st = k + 6; if (s.charAt(st) === "\r") st++; if (s.charAt(st) === "\n") st++;
      var en = s.indexOf("endstream", st); if (en < 0) break;
      var data = u8.subarray(st, en);
      pos = en + 9;
      if (/FlateDecode/.test(dict)) {
        jobs.push(cmpInflate(data).catch(function () { return null; }));
      } else if (dict.indexOf("/Subtype") < 0 || dict.indexOf("/Image") < 0) {
        jobs.push(Promise.resolve(data));
      }
    }
    return Promise.all(jobs).then(function (list) {
      return list.filter(Boolean).map(CMP_LATIN1).filter(function (t) { return /\bBT\b/.test(t) && /\bT[jJ]\b/.test(t); });
    });
  }
  function cmpParseContent(t, page, out) {
    var i = 0, n = t.length, st = [], lx = 0, ly = 0, x = 0, y = 0, lead = 0;
    function lit() {
      var d = 1, r = "";
      i++;
      while (i < n && d > 0) {
        var c = t.charAt(i);
        if (c === "\\") {
          var m = t.charAt(i + 1);
          if (m === "n") r += "\n"; else if (m === "r" || m === "t" || m === "b" || m === "f") r += " ";
          else if (/[0-7]/.test(m)) { var o = t.substr(i + 1, 3).match(/^[0-7]{1,3}/)[0]; r += String.fromCharCode(parseInt(o, 8)); i += o.length; }
          else r += m;
          i += 2; continue;
        }
        if (c === "(") d++;
        else if (c === ")") { d--; if (!d) { i++; break; } }
        r += c; i++;
      }
      return r;
    }
    function push(s) { out.push({ p: page, x: x, y: y, t: s }); }
    while (i < n) {
      var c = t.charAt(i);
      if (/\s/.test(c)) { i++; continue; }
      if (c === "(") { st.push({ s: lit() }); continue; }
      if (c === "<" && t.charAt(i + 1) !== "<") {
        var e = t.indexOf(">", i), hx = t.slice(i + 1, e).replace(/\s/g, ""), r = "";
        for (var h = 0; h + 1 < hx.length; h += 2) r += String.fromCharCode(parseInt(hx.substr(h, 2), 16));
        i = e + 1; st.push({ s: r }); continue;
      }
      if (c === "[") {
        i++; var arr = [];
        while (i < n && t.charAt(i) !== "]") {
          if (t.charAt(i) === "(") arr.push(lit()); else i++;
        }
        i++; st.push({ a: arr }); continue;
      }
      if (c === "/") { var m2 = t.slice(i + 1).match(/^[^\s\/\[\]()<>]*/)[0]; i += 1 + m2.length; st.push({ nm: m2 }); continue; }
      if (c === "<" || c === ">") { i += 2; continue; }
      var w = t.slice(i).match(/^[^\s\/\[\]()<>]+/)[0]; i += w.length;
      if (/^[-+.\d]/.test(w) && !isNaN(Number(w))) { st.push({ v: Number(w) }); continue; }
      var v = st.map(function (q) { return q.v; });
      if (w === "BT") { lx = ly = x = y = 0; }
      else if (w === "Td" || w === "TD") { lx += v[0] || 0; ly += v[1] || 0; x = lx; y = ly; if (w === "TD") lead = -(v[1] || 0); }
      else if (w === "Tm") { lx = x = v[4] || 0; ly = y = v[5] || 0; }
      else if (w === "TL") lead = v[0] || 0;
      else if (w === "T*") { ly -= lead; y = ly; }
      else if (w === "Tj") { var q0 = st[st.length - 1]; if (q0 && q0.s !== undefined) push(q0.s); }
      else if (w === "TJ") { var q1 = st[st.length - 1]; if (q1 && q1.a) push(q1.a.join("")); }
      else if (w === "'" || w === '"') { ly -= lead; y = ly; var q2 = st[st.length - 1]; if (q2 && q2.s !== undefined) push(q2.s); }
      st = [];
    }
  }
  function cmpIso(s) {
    var m = s.match(/^(\d{1,2})\/(\d{1,2})\/(\d{4})$/);
    return m ? m[3] + "-" + ("0" + m[2]).slice(-2) + "-" + ("0" + m[1]).slice(-2) : null;
  }
  function cmpRead(buf) {
    return cmpStreams(new Uint8Array(buf)).then(function (pages) {
      var items = [];
      pages.forEach(function (t, p) { cmpParseContent(t, p, items); });
      if (!items.length) return null;
      items.sort(function (a, b) { return a.p - b.p || b.y - a.y || a.x - b.x; });
      var lines = [], cur = null;
      items.forEach(function (it) {
        if (cur && cur.p === it.p && Math.abs(cur.y - it.y) < 2) cur.its.push(it);
        else { cur = { p: it.p, y: it.y, its: [it] }; lines.push(cur); }
      });
      lines.forEach(function (l) { l.its.sort(function (a, b) { return a.x - b.x; }); });
      var res = { name: null, duty: [], adv: [], final: null, any: false };
      var f0 = lines[0], ft = f0 ? f0.its.map(function (z) { return z.t; }).join(" ").trim() : "";
      var nm = ft.match(/^Name\s*:\s*(.*)$/i);
      if (nm) res.name = nm[1].trim();
      else if (f0 && f0.its.length === 1 && !cmpIso(ft) && ft.indexOf("Rs.") < 0) res.name = ft;
      if (res.name !== null && /^_*$/.test(res.name)) res.name = "";
      lines.forEach(function (l) {
        var txt = l.its.map(function (z) { return z.t; }).join(" ");
        var fm = txt.match(/Final Payment\s*=\s*(-?)Rs\.\s?([\d,]+)/);
        if (fm) res.final = (fm[1] ? -1 : 1) * Number(fm[2].replace(/,/g, ""));
        var d0 = l.its[0], iso = d0 && d0.x < 90 ? cmpIso(d0.t.trim()) : null;
        if (!iso) return;
        var amt = null, half = 0, full = 0, loc = [];
        l.its.slice(1).forEach(function (z) {
          var t = z.t.trim(), am = t.match(/^Rs\.\s?([\d,]+(?:\.\d+)?)$/);
          if (am) { if (amt === null) amt = Number(am[1].replace(/,/g, "")); }
          else if (t === "1") { if (z.x / 2.8346 < 166) half++; else full++; }
          else if (t) loc.push(t);
        });
        if (amt !== null) { res.adv.push({ date: iso, amount: amt }); res.any = true; }
        else if (half || full) { res.duty.push({ date: iso, h: half, f: full, loc: loc.join(" ") }); res.any = true; }
      });
      return res;
    });
  }
  function cmpCompare(emp, pdf) {
    var dmDuty = state.records.filter(function (r) { return r.names.indexOf(emp.name) >= 0; })
      .map(function (r) { return { date: r.date, h: r.duty === "Half" ? 1 : 0, f: r.duty === "Full" ? 1 : 0, loc: r.loc || "" }; });
    var dmAdv = state.advances.filter(function (a) { return a.empId === emp.id; }).map(function (a) { return { date: a.date, amount: a.amount }; });
    function by(list) { var m = {}; list.forEach(function (r) { (m[r.date] = m[r.date] || []).push(r); }); return m; }
    function keys(a, b) { var k = {}; Object.keys(a).concat(Object.keys(b)).forEach(function (d) { k[d] = 1; }); return Object.keys(k).sort(); }
    function sum(l, f) { return l.reduce(function (s, r) { return s + r[f]; }, 0); }
    var out = { duty: [], adv: [], good: 0, bad: 0 }, pd = by(pdf.duty), dd = by(dmDuty);
    keys(pd, dd).forEach(function (d) {
      var p = pd[d] || [], m = dd[d] || [];
      if (p.length && sum(p, "h") === sum(m, "h") && sum(p, "f") === sum(m, "f")) {
        m.forEach(function (r) { out.duty.push({ k: "ok", date: d, h: r.h, f: r.f, loc: r.loc }); out.good++; });
      } else {
        p.forEach(function (r) { for (var j = 0; j < Math.max(1, r.h + r.f); j++) { out.duty.push({ k: "bad", date: d, h: r.h ? 1 : 0, f: r.f ? 1 : 0, loc: r.loc }); out.bad++; } });
        m.forEach(function (r) { out.duty.push({ k: "fix", date: d, h: r.h, f: r.f, loc: r.loc }); out.good++; });
      }
    });
    var pa = by(pdf.adv), da = by(dmAdv);
    keys(pa, da).forEach(function (d) {
      var p = pa[d] || [], m = da[d] || [];
      if (p.length && sum(p, "amount") === sum(m, "amount")) {
        p.forEach(function (r) { out.adv.push({ k: "ok", date: d, amount: r.amount }); out.good++; });
      } else {
        p.forEach(function (r) { out.adv.push({ k: "bad", date: d, amount: r.amount }); out.bad++; });
        m.forEach(function (r) { out.adv.push({ k: "fix", date: d, amount: r.amount }); out.good++; });
      }
    });
    out.pdfAdv = sum(pdf.adv, "amount"); out.dmAdv = sum(dmAdv, "amount");
    out.hd = dmDuty.filter(function (r) { return r.h; }).length; out.fd = dmDuty.filter(function (r) { return r.f; }).length;
    out.rh = rateOf(emp, "Half"); out.rf = rateOf(emp, "Full");
    out.hAmt = out.hd * out.rh; out.fAmt = out.fd * out.rf;
    out.gross = out.hAmt + out.fAmt; out.sub = out.gross - out.dmAdv; out.net = out.sub;
    out.pdfFinal = pdf.final;
    return out;
  }
  function cmpMakePdf(emp, r) {
    var doc = new window.jspdf.jsPDF({ unit: "mm", format: "a4" });
    var W = doc.internal.pageSize.getWidth(), TW = W - 28 - 9, money = pdfMoney;
    function hooks(widths) {
      return {
        parse: function (d) {
          var t = d.cell.text.join(" ");
          if (!pdfUni(t)) return;
          var hd = d.section === "head", ctr = hd || (d.section === "body" && d.column.index > 1 && widths.length > 2);
          var meta = d.section === "body" ? d.row.__m : null;
          var bg = hd ? "#1e8259" : (meta && meta.k === "fix") ? "#eaf3de" : "#ffffff";
          var im = pdfTextImg(t, widths[d.column.index] - 6, 10, hd ? "#ffffff" : "#282828", hd, bg, ctr);
          d.cell.__img = im; d.cell.text = [""];
          d.cell.styles.minCellHeight = Math.max(d.cell.styles.minCellHeight || 0, im.h + 6);
        },
        draw: function (d) {
          if (d.cell.__img) doc.addImage(d.cell.__img.data, "PNG", d.cell.x + 3, d.cell.y + 3, d.cell.__img.w, d.cell.__img.h);
        }
      };
    }
    function mark(x, y, ok) {
      doc.setLineWidth(0.2);
      if (ok) doc.setFillColor(30, 130, 89); else doc.setFillColor(217, 48, 37);
      doc.roundedRect(x, y, 5, 5, 1, 1, "F");
      doc.setDrawColor(255, 255, 255); doc.setLineWidth(0.7);
      if (ok) { doc.line(x + 1.1, y + 2.7, x + 2.2, y + 3.8); doc.line(x + 2.2, y + 3.8, x + 3.9, y + 1.3); }
      else { doc.line(x + 1.3, y + 1.3, x + 3.7, y + 3.7); doc.line(x + 3.7, y + 1.3, x + 1.3, y + 3.7); }
      doc.setLineWidth(0.2);
    }
    function tableStyle(metaList, widths, h) {
      return {
        didParseCell: function (d) {
          if (d.section === "body") {
            d.row.__m = metaList[d.row.index];
            var m = d.row.__m;
            if (m && m.k === "fix") d.cell.styles.fillColor = [234, 243, 222];
            if (m && m.tot) { d.cell.styles.fontStyle = "bold"; if (m.k !== "fix") d.cell.styles.fillColor = [231, 236, 243]; }
          }
          if (widths.length === 4 && d.column.index > 1) d.cell.styles.halign = "center";
          if (widths.length === 2 && d.column.index === 1) d.cell.styles.halign = "right";
          h.parse(d);
        },
        didDrawCell: function (d) {
          h.draw(d);
          var m = d.section === "body" ? d.row.__m : null;
          if (!m) return;
          if (m.k === "bad" && d.column.index === widths.length - 1) {
            doc.setDrawColor(217, 48, 37); doc.setLineWidth(0.5);
            doc.line(14, d.cell.y + d.cell.height / 2, 14 + TW, d.cell.y + d.cell.height / 2);
            doc.setLineWidth(0.2);
          }
          if (d.column.index === 0) mark(14 + TW + 2.2, d.cell.y + d.cell.height / 2 - 2.5, m.k !== "bad");
        }
      };
    }
    doc.setFillColor(67, 56, 202); doc.rect(0, 0, W, 26, "F");
    doc.setTextColor(255, 255, 255); doc.setFont("helvetica", "bold"); doc.setFontSize(18);
    var nameText = PS("Name") + ": " + emp.name;
    if (pdfUni(nameText)) { var ni = pdfTextImg(nameText, W - 28, 18, "#ffffff", true, "#4338ca", true); doc.addImage(ni.data, "PNG", 14, 13 - ni.h / 2, ni.w, ni.h); }
    else doc.text(nameText, W / 2, 17, { align: "center" });
    var w1 = [32, TW - 32 - 52, 26, 26], h1 = hooks(w1);
    var common = { theme: "grid", headStyles: { fillColor: [30, 130, 89], textColor: 255, fontStyle: "bold", fontSize: 10 }, bodyStyles: { fillColor: [255, 255, 255], fontStyle: "normal" }, styles: { font: "helvetica", fontSize: 10, cellPadding: 3, textColor: [40, 40, 40], lineColor: [200, 205, 210], lineWidth: 0.2 }, margin: { left: 14, right: 23 }, tableWidth: TW };
    var ts1 = tableStyle(r.duty, w1, h1);
    doc.autoTable(Object.assign({ startY: 34, head: [[PS("Date"), PS("Location/Work"), PS("Half Day"), PS("Full Day")]],
      body: r.duty.map(function (x) { return [pdfDate(x.date), x.loc || "-", x.h ? "1" : "", x.f ? "1" : ""]; }),
      columnStyles: { 0: { cellWidth: 32 }, 1: { cellWidth: "auto" }, 2: { cellWidth: 26 }, 3: { cellWidth: 26 } } }, common, ts1));
    var y = doc.lastAutoTable.finalY + 10;
    if (r.adv.length) {
      if (y > 255) { doc.addPage(); y = 20; }
      doc.setFont("helvetica", "bold"); doc.setFontSize(13); doc.setTextColor(30, 130, 89);
      var ah = PS("Advance amount");
      if (pdfUni(ah)) { var ai = pdfTextImg(ah, W - 40, 13, "#1e8259", true, "#ffffff", false); doc.addImage(ai.data, "PNG", 14, y - 4.6, ai.w, ai.h); } else doc.text(ah, 14, y);
      var rows = r.adv.slice(), tm = r.adv.slice();
      if (r.pdfAdv !== r.dmAdv) {
        rows.push({ k: "bad", tot: 1, amount: r.pdfAdv }); rows.push({ k: "fix", tot: 1, amount: r.dmAdv });
      } else rows.push({ k: "ok", tot: 1, amount: r.dmAdv });
      var w2 = [TW / 2, TW / 2], h2 = hooks(w2);
      doc.autoTable(Object.assign({ startY: y + 3, head: [[PS("Date"), PS("Amount")]],
        body: rows.map(function (x) { return [x.tot ? PS("Total Advance") : pdfDate(x.date), money(x.amount)]; }),
        columnStyles: { 0: { cellWidth: TW / 2 }, 1: { cellWidth: TW / 2 } } }, common, tableStyle(rows, w2, h2)));
      y = doc.lastAutoTable.finalY + 10;
    }
    var diff = r.pdfFinal !== null && r.pdfFinal !== r.net;
    var bh = diff ? 90 : 78;
    if (y + bh + 12 > 285) { doc.addPage(); y = 20; }
    function line(str, x, yy, pt, bold, rgb) {
      if (!pdfUni(str)) { doc.setFont("helvetica", bold ? "bold" : "normal"); doc.setFontSize(pt); doc.setTextColor(rgb[0], rgb[1], rgb[2]); doc.text(str, x, yy); return; }
      var hex = "#" + rgb.map(function (n) { return ("0" + n.toString(16)).slice(-2); }).join("");
      var im = pdfTextImg(str, W - 40, pt, hex, bold, "#ffffff", false);
      doc.addImage(im.data, "PNG", x, yy - pt * 0.3528 * 1.05, im.w, im.h);
    }
    line("Correct bill (from your records)", 14, y, 13, true, [30, 130, 89]);
    y += 4;
    doc.setDrawColor(15, 118, 110); doc.setLineWidth(0.6); doc.roundedRect(14, y, W - 28, bh, 3, 3, "S"); doc.setLineWidth(0.2);
    var ink = [23, 35, 59], teal = [15, 118, 110];
    line(PS("Half Days") + ": " + r.hd + "  (" + r.hd + " x " + money(r.rh) + " = " + money(r.hAmt) + ")", 20, y + 11, 12, false, ink);
    line(PS("Full Days") + ": " + r.fd + "  (" + r.fd + " x " + money(r.rf) + " = " + money(r.fAmt) + ")", 20, y + 20, 12, false, ink);
    line(PS("Total Payment") + ": " + money(r.gross), 20, y + 29, 12, false, ink);
    line(PS("Advance") + ": - " + money(r.dmAdv), 20, y + 38, 12, false, ink);
    line(money(r.gross) + " - " + money(r.dmAdv) + " = " + money(r.sub), 20, y + 47, 12, false, ink);
    line(money(r.sub) + " + " + money(0) + " (" + PS("Pending payment") + ")", 20, y + 58, 12, false, ink);
    var fy = y + 68;
    if (diff) {
      var ot = PS("Final Payment") + " = " + money(r.pdfFinal);
      line(ot, 20, y + 68, 11, false, [217, 48, 37]);
      doc.setDrawColor(217, 48, 37); doc.setLineWidth(0.4); doc.line(20, y + 66.7, 20 + doc.getTextWidth(ot) * 0.95, y + 66.7); doc.setLineWidth(0.2);
      fy = y + 79;
    }
    line(PS("Final Payment") + " = " + money(r.net), 20, fy, 16, true, teal);
    return doc;
  }
  function cmpHide() { $("cmpsheet").hidden = true; document.body.style.overflow = ""; }
  function cmpShow(emp, r, doc) {
    var buf = doc.output("arraybuffer"), blob = new Blob([buf], { type: "application/pdf" });
    if (cmpUrl) URL.revokeObjectURL(cmpUrl);
    cmpUrl = URL.createObjectURL(blob);
    var fname = (emp.name.replace(/[^A-Za-z0-9]+/g, "-").replace(/^-|-$/g, "") || "Employee") + "-corrected-" + today() + ".pdf";
    $("cmptitle").textContent = emp.name;
    $("cmpsub").textContent = r.good + " correct, " + r.bad + " wrong or missing";
    var box = $("cmplist"); box.innerHTML = "";
    function add(k, a, b) {
      var d = document.createElement("div"); d.className = "cmprow " + k;
      var s1 = document.createElement("span"), s2 = document.createElement("span"), s3 = document.createElement("span");
      s1.textContent = a; s2.textContent = b; s3.textContent = k === "bad" ? "❌" : "✅";
      d.appendChild(s1); d.appendChild(s2); d.appendChild(s3); box.appendChild(d);
    }
    function head(t) { var h = document.createElement("div"); h.className = "cmph"; h.textContent = t; box.appendChild(h); }
    head("Duty");
    r.duty.forEach(function (x) { add(x.k, fmt(x.date), (x.f ? "Full" : "Half") + (x.loc ? " · " + x.loc : "")); });
    if (r.adv.length) { head("Advance"); r.adv.forEach(function (x) { add(x.k, fmt(x.date), money(x.amount)); }); }
    $("cmpfinal").textContent = "Final Payment from your records: " + money(r.net);
    var dl = $("cmpdl");
    dl.onclick = function () {
      var a = document.createElement("a"); a.href = cmpUrl; a.download = fname; a.textContent = "x";
      a.style.display = "none"; document.body.appendChild(a); a.click();
      setTimeout(function () { if (a.parentNode) a.parentNode.removeChild(a); }, 1500);
    };
    $("cmpsheet").hidden = false; document.body.style.overflow = "hidden";
  }
  function cmpNames() { return state.employees.map(function (e) { return e.name; }); }
  function cmpList() {
    var q = $("cname").value.trim().toLowerCase(), ul = $("clist"); ul.innerHTML = "";
    var names = cmpNames().filter(function (n) { return n.toLowerCase().indexOf(q) >= 0; }).sort(function (a, b) {
      var sa = a.toLowerCase().indexOf(q) === 0 ? 0 : 1, sb = b.toLowerCase().indexOf(q) === 0 ? 0 : 1; return sa - sb || a.localeCompare(b);
    });
    if (!names.length) { var none = document.createElement("li"); none.className = "none"; none.textContent = tx("no_match"); ul.appendChild(none); }
    names.forEach(function (n) {
      var li = document.createElement("li"); li.setAttribute("role", "option"); li.textContent = n;
      li.onmousedown = function (e) { e.preventDefault(); };
      li.onclick = function () { cmpPick(n); };
      ul.appendChild(li);
    });
    ul.hidden = false; $("cname").setAttribute("aria-expanded", "true");
  }
  function cmpHideList() { $("clist").hidden = true; $("cname").setAttribute("aria-expanded", "false"); }
  function cmpPick(n) {
    cmpEmp = state.employees.filter(function (e) { return e.name === n; })[0] || null;
    $("cname").value = n; cmpHideList(); $("cname").blur();
    cmpBuf = null; $("cfname").textContent = ""; $("cmsg").textContent = ""; $("cmsg").className = "msg";
    $("cstep").hidden = !cmpEmp;
  }
  $("cname").addEventListener("input", function () { cmpEmp = null; cmpBuf = null; $("cstep").hidden = true; $("cmsg").textContent = ""; cmpList(); });
  $("cname").addEventListener("focus", cmpList);
  $("cname").addEventListener("blur", function () { setTimeout(cmpHideList, 150); });
  $("cpick").onclick = function () { $("cfile").value = ""; $("cfile").click(); };
  $("cfile").onchange = function () {
    var f = this.files && this.files[0], msg = $("cmsg");
    msg.textContent = ""; msg.className = "msg";
    if (!f) return;
    if (f.size > 10 * 1024 * 1024) { cmpBuf = null; $("cfname").textContent = ""; return say(msg, "This PDF is too big. Use a PDF made by BillKarta.", true); }
    var rd = new FileReader();
    rd.onerror = function () { cmpBuf = null; say(msg, "Couldn't read that file. Try again.", true); };
    rd.onload = function () { cmpBuf = rd.result; $("cfname").textContent = f.name; };
    rd.readAsArrayBuffer(f);
  };
  $("cgo").onclick = function () {
    var msg = $("cmsg"); msg.textContent = ""; msg.className = "msg";
    if (!cmpEmp) return say(msg, "Select an employee first.", true);
    if (!cmpBuf) return say(msg, "Choose a PDF first.", true);
    if (!window.jspdf || !window.jspdf.jsPDF || !window.jspdf.jsPDF.API.autoTable) return say(msg, tx("pdf_nolib"), true);
    if (typeof DecompressionStream === "undefined") { /* very old WebView: plain PDFs still work */ window.DecompressionStream = undefined; }
    cmpRead(cmpBuf).then(function (pdf) {
      if (!pdf || !pdf.any) return say(msg, "Couldn't read duties or advances in this PDF. Use a PDF made by BillKarta.", true);
      var norm = function (s) { return String(s).toLowerCase().replace(/\s+/g, " ").trim(); };
      if (pdf.name && norm(pdf.name) !== norm(cmpEmp.name)) return say(msg, "This PDF is for “" + pdf.name + "”, not “" + cmpEmp.name + "”. Choose the right PDF.", true);
      var r = cmpCompare(cmpEmp, pdf), doc = cmpMakePdf(cmpEmp, r);
      cmpShow(cmpEmp, r, doc);
      if (!pdf.name) say(msg, "The name in this PDF couldn't be read, so it was compared with " + cmpEmp.name + ".");
    }).catch(function () { say(msg, "Couldn't compare this PDF. Use a PDF made by BillKarta.", true); });
  };
  $("cmpx").onclick = cmpHide;
  $("cmpsheet").onclick = function (e) { if (e.target === $("cmpsheet")) cmpHide(); };

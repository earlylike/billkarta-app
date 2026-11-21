#!/usr/bin/env python3
"""App-only: adds an "Advance" table (Date / Amount, with a Total row at the end) to the employee bill PDF
made on the Duty Manager page, like the Personal PDF. Placed after the duty table and before the summary box.
Usage: patch_forall_pdf_adv.py <assets/www folder>   (idempotent; run by sync-pages.sh)"""
import os, sys
MARK = "BK-EMP-ADV-PDF"
p = os.path.join(sys.argv[1], "forall", "index.html")
s = open(p, encoding="utf-8").read()
if MARK in s:
    print("employee PDF advance table already patched"); sys.exit(0)

OLD1 = "billData = { name: billName, rows: rows,"
NEW1 = ("billData = { /* BK-EMP-ADV-PDF */ advRows: (emp ? state.advances.filter(function (a) { return a.empId === emp.id; })"
        ".sort(function (a, b) { return a.date < b.date ? -1 : a.date > b.date ? 1 : 0; }) : []), name: billName, rows: rows,")
assert s.count(OLD1) == 1
s = s.replace(OLD1, NEW1, 1)

OLD2 = "    y += 8;\n    var gross = b.hAmt + b.fAmt;"
BLOCK = """    y += 8;
    if (b.advRows && b.advRows.length) {
      var ahead = function () {
        doc.setFillColor(26, 127, 86); doc.rect(M, y, tw, 9, "F");
        put(doc, tx("date"), M + 2, y + 6, { size: 10, bold: true, color: "#ffffff" });
        put(doc, tx("amount"), M + tw - 2, y + 6, { size: 10, bold: true, color: "#ffffff", align: "right" });
        y += 9;
        doc.setFont("helvetica", "normal"); doc.setTextColor(30, 30, 30); doc.setDrawColor(170, 180, 175);
      };
      if (y + 30 > H - 20) { doc.addPage(); y = 20; }
      put(doc, tx("advance"), M, y, { size: 13, bold: true, color: "#1e8259" });
      y += 3;
      ahead();
      var advSum = 0;
      b.advRows.forEach(function (a) {
        if (y + 8 > H - 20) { doc.addPage(); y = 20; ahead(); }
        advSum += a.amount;
        doc.rect(M, y, tw / 2, 8); doc.rect(M + tw / 2, y, tw / 2, 8);
        doc.setFont("helvetica", "normal"); doc.setFontSize(10); doc.setTextColor(30, 30, 30);
        doc.text(fmt(a.date), M + 2, y + 5.5);
        put(doc, money(a.amount), M + tw - 2, y + 5.5, { size: 10, color: "#1e1e1e", align: "right" });
        y += 8;
      });
      if (y + 9 > H - 20) { doc.addPage(); y = 20; ahead(); }
      doc.setFillColor(231, 236, 243); doc.setDrawColor(170, 180, 175); doc.rect(M, y, tw, 9, "FD");
      put(doc, tx("total"), M + 2, y + 6, { size: 10, bold: true, color: "#282828" });
      put(doc, money(advSum), M + tw - 2, y + 6, { size: 10, bold: true, color: "#282828", align: "right" });
      y += 9 + 8;
    }
    var gross = b.hAmt + b.fAmt;"""
assert s.count(OLD2) == 1
s = s.replace(OLD2, BLOCK, 1)
open(p, "w", encoding="utf-8").write(s)
print("patched employee bill PDF advance table")

  /* BK-PDF-STYLE: same layout as the Personal PDF */
  var PDF_S = {"Name": {"hi": "नाम", "mr": "नाव", "gu": "નામ", "pa": "ਨਾਂ", "ta": "பெயர்", "te": "పేరు", "kn": "ಹೆಸರು"}, "Date": {"mr": "तारीख", "hi": "तारीख", "gu": "તારીખ", "pa": "ਤਾਰੀਖ", "ta": "தேதி", "te": "తేదీ", "kn": "ದಿನಾಂಕ"}, "Amount": {"mr": "रक्कम", "hi": "राशि", "gu": "રકમ", "pa": "ਰਕਮ", "ta": "தொகை", "te": "మొత్తం", "kn": "ಮೊತ್ತ"}, "Advance amount": {"mr": "अॅडव्हान्स रक्कम", "hi": "एडवांस राशि", "gu": "એડવાન્સ રકમ", "pa": "ਐਡਵਾਂਸ ਰਕਮ", "ta": "முன்பணத் தொகை", "te": "అడ్వాన్స్ మొత్తం", "kn": "ಅಡ್ವಾನ್ಸ್ ಮೊತ್ತ"}, "Total Advance": {"mr": "एकूण अॅडव्हान्स", "hi": "कुल एडवांस", "gu": "કુલ એડવાન્સ", "pa": "ਕੁੱਲ ਐਡਵਾਂਸ", "ta": "மொத்த முன்பணம்", "te": "మొత్తం అడ్వాన్స్", "kn": "ಒಟ್ಟು ಅಡ್ವಾನ್ಸ್"}, "Total Payment": {"hi": "कुल भुगतान", "mr": "एकूण देय", "gu": "કુલ ચુકવણી", "pa": "ਕੁੱਲ ਭੁਗਤਾਨ", "ta": "மொத்தப் பணம்", "te": "మొత్తం చెల్లింపు", "kn": "ಒಟ್ಟು ಪಾವತಿ"}, "Advance": {"mr": "उचल", "hi": "एडवांस", "gu": "એડવાન્સ", "pa": "ਐਡਵਾਂਸ", "ta": "முன்பணம்", "te": "అడ్వాన్స్", "kn": "ಅಡ್ವಾನ್ಸ್"}, "Half Days": {"mr": "अर्धे दिवस", "hi": "आधे दिन", "gu": "અડધા દિવસ", "pa": "ਅੱਧੇ ਦਿਨ", "ta": "அரை நாட்கள்", "te": "అర్ధ రోజులు", "kn": "ಅರ್ಧ ದಿನಗಳು"}, "Full Days": {"mr": "पूर्ण दिवस", "hi": "पूरे दिन", "gu": "પૂરા દિવસ", "pa": "ਪੂਰੇ ਦਿਨ", "ta": "முழு நாட்கள்", "te": "పూర్తి రోజులు", "kn": "ಪೂರ್ಣ ದಿನಗಳು"}, "Pending payment": {"mr": "प्रलंबित रक्कम", "hi": "बकाया राशि", "gu": "બાકી ચુકવણી", "pa": "ਬਕਾਇਆ ਭੁਗਤਾਨ", "ta": "நிலுவைத் தொகை", "te": "పెండింగ్ చెల్లింపు", "kn": "ಬಾಕಿ ಪಾವತಿ"}, "Final Payment": {"mr": "अंतिम देय रक्कम", "hi": "अंतिम भुगतान", "gu": "અંતિમ ચુકવણી", "pa": "ਅੰਤਿਮ ਭੁਗਤਾਨ", "ta": "இறுதிப் பணம்", "te": "తుది చెల్లింపు", "kn": "ಅಂತಿಮ ಪಾವತಿ"}, "Location/Work": {"hi": "जगह/काम", "mr": "ठिकाण/काम", "gu": "સ્થળ/કામ", "pa": "ਥਾਂ/ਕੰਮ", "ta": "இடம்/வேலை", "te": "స్థలం/పని", "kn": "ಸ್ಥಳ/ಕೆಲಸ"}, "Half Day": {"mr": "अर्धा दिवस", "hi": "आधा दिन", "gu": "અડધો દિવસ", "pa": "ਅੱਧਾ ਦਿਨ", "ta": "அரை நாள்", "te": "అర్ధ రోజు", "kn": "ಅರ್ಧ ದಿನ"}, "Full Day": {"mr": "पूर्ण दिवस", "hi": "पूरा दिन", "gu": "પૂરો દિવસ", "pa": "ਪੂਰਾ ਦਿਨ", "ta": "முழு நாள்", "te": "పూర్తి రోజు", "kn": "ಪೂರ್ಣ ದಿನ"}};
  function PS(en) { var m = PDF_S[en]; return lang !== "en" && m && m[lang] ? m[lang] : en; }
  function pdfUni(str) { return /[^\x20-\x7e]/.test(str || ""); }
  function pdfTextImg(str, mmW, pt, color, bold, bg, center) {
    var K = 12, px = pt * 0.3528 * K, lh = px * 1.5;
    var c = document.createElement("canvas"), x = c.getContext("2d");
    var fnt = (bold ? "700 " : "400 ") + px + "px " + FONT_FAMILY;
    x.font = fnt;
    var lines = [], cur = "";
    String(str).split(/\s+/).forEach(function (w) {
      var t = cur ? cur + " " + w : w;
      if (cur && x.measureText(t).width > mmW * K) { lines.push(cur); cur = w; } else { cur = t; }
    });
    if (cur) lines.push(cur);
    c.width = Math.ceil(mmW * K);
    c.height = Math.ceil(lines.length * lh + px * 0.3);
    x.fillStyle = bg; x.fillRect(0, 0, c.width, c.height);
    x.font = fnt; x.fillStyle = color; x.textBaseline = "top"; x.textAlign = center ? "center" : "left";
    lines.forEach(function (l, i) { x.fillText(l, center ? c.width / 2 : 0, i * lh + px * 0.2); });
    return { data: c.toDataURL("image/png"), w: mmW, h: c.height / K };
  }
  function pdfMoney(n) { return (n < 0 ? "-" : "") + "Rs." + Math.abs(n).toLocaleString("en-IN"); }
  function pdfDate(iso) { var p = iso.split("-"); return p[2] + "/" + p[1] + "/" + p[0]; }
  var billData = null;
  function makePdf() {
    var b = billData, msg = $("pmsg");
    if (!b) return;
    if (!window.jspdf || !window.jspdf.jsPDF || !window.jspdf.jsPDF.API.autoTable) return say(msg, tx("pdf_nolib"), true);
    var doc = new window.jspdf.jsPDF({ unit: "mm", format: "a4" });
    var W = doc.internal.pageSize.getWidth();
    var money = pdfMoney;
    function cellHooks(widths) {
      return {
        parse: function (d) {
          var t = d.cell.text.join(" ");
          if (!pdfUni(t)) return;
          var hd = d.section === "head", ft = d.section === "foot";
          var ctr = hd || (d.section === "body" && d.column.index > 1 && widths.length > 2);
          var im = pdfTextImg(t, widths[d.column.index] - 6, 10, hd ? "#ffffff" : "#282828", hd || ft, hd ? "#1e8259" : ft ? "#e7ecf3" : "#ffffff", ctr);
          d.cell.__img = im;
          d.cell.text = [""];
          d.cell.styles.minCellHeight = Math.max(d.cell.styles.minCellHeight || 0, im.h + 6);
        },
        draw: function (d) {
          if (d.cell.__img) doc.addImage(d.cell.__img.data, "PNG", d.cell.x + 3, d.cell.y + 3, d.cell.__img.w, d.cell.__img.h);
        }
      };
    }
    function line(str, x, y, pt, bold, rgb) {
      if (!pdfUni(str)) {
        doc.setFont("helvetica", bold ? "bold" : "normal"); doc.setFontSize(pt); doc.setTextColor(rgb[0], rgb[1], rgb[2]);
        doc.text(str, x, y);
        return;
      }
      var hex = "#" + rgb.map(function (n) { return ("0" + n.toString(16)).slice(-2); }).join("");
      var im = pdfTextImg(str, W - 28 - 12, pt, hex, bold, "#ffffff", false);
      doc.addImage(im.data, "PNG", x, y - pt * 0.3528 * 1.05, im.w, im.h);
    }
    doc.setFillColor(67, 56, 202);
    doc.rect(0, 0, W, 26, "F");
    doc.setTextColor(255, 255, 255);
    doc.setFont("helvetica", "bold");
    doc.setFontSize(18);
    var nameText = PS("Name") + ": " + (b.name || "____________________");
    if (pdfUni(nameText)) {
      var ni = pdfTextImg(nameText, W - 28, 18, "#ffffff", true, "#4338ca", true);
      doc.addImage(ni.data, "PNG", 14, 13 - ni.h / 2, ni.w, ni.h);
    } else { doc.text(nameText, W / 2, 17, { align: "center" }); }
    var h1 = cellHooks([32, W - 28 - 88, 28, 28]);
    doc.autoTable({
      startY: 34,
      margin: { left: 14, right: 14 },
      tableWidth: W - 28,
      head: [[PS("Date"), PS("Location/Work"), PS("Half Day"), PS("Full Day")]],
      body: b.rows.map(function (r) { return [pdfDate(r.date), r.loc || "-", r.duty === "Half" ? "1" : "", r.duty === "Full" ? "1" : ""]; }),
      theme: "grid",
      headStyles: { fillColor: [30, 130, 89], textColor: 255, fontStyle: "bold", fontSize: 10 },
      bodyStyles: { fillColor: [255, 255, 255], fontStyle: "normal" },
      styles: { font: "helvetica", fontSize: 10, cellPadding: 3, textColor: [40, 40, 40], lineColor: [200, 205, 210], lineWidth: 0.2 },
      columnStyles: { 0: { cellWidth: 32 }, 1: { cellWidth: "auto" }, 2: { cellWidth: 28 }, 3: { cellWidth: 28 } },
      didDrawCell: function (d) { h1.draw(d); },
      didParseCell: function (d) {
        if (d.column.index > 1) d.cell.styles.halign = "center";
        h1.parse(d);
      }
    });
    var advRows = b.advRows || [], advSum = 0;
    advRows.forEach(function (a) { advSum += a.amount; });
    if (advRows.length) {
      var ay = doc.lastAutoTable.finalY + 10;
      if (ay > 260) { doc.addPage(); ay = 20; }
      line(PS("Advance amount"), 14, ay, 13, true, [30, 130, 89]);
      var h2 = cellHooks([91, 91]);
      doc.autoTable({
        startY: ay + 3,
        margin: { left: 14, right: 14 },
        head: [[PS("Date"), PS("Amount")]],
        body: advRows.map(function (a) { return [pdfDate(a.date), money(a.amount)]; }),
        foot: [[PS("Total Advance"), money(advSum)]], showFoot: "lastPage",
        columnStyles: { 0: { cellWidth: 91 }, 1: { cellWidth: 91 } },
        theme: "grid",
        headStyles: { fillColor: [30, 130, 89], textColor: 255, fontStyle: "bold", fontSize: 10 },
        footStyles: { fillColor: [231, 236, 243], textColor: [40, 40, 40], fontStyle: "bold" },
        styles: { font: "helvetica", fontSize: 10, cellPadding: 3, textColor: [40, 40, 40], lineColor: [200, 205, 210], lineWidth: 0.2 },
        didDrawCell: function (d) { h2.draw(d); },
        didParseCell: function (d) { if (d.column.index === 1) d.cell.styles.halign = "right"; h2.parse(d); }
      });
    }
    var y = doc.lastAutoTable.finalY + 10;
    if (y > 195) { doc.addPage(); y = 20; }
    doc.setDrawColor(15, 118, 110);
    doc.setLineWidth(0.6);
    doc.roundedRect(14, y, W - 28, 78, 3, 3, "S");
    var ink = [23, 35, 59], teal = [15, 118, 110];
    var gross = b.hAmt + b.fAmt, net1 = gross - b.adv;
    line(PS("Half Days") + ": " + b.hd + "  (" + b.hd + " x " + money(b.rh) + " = " + money(b.hAmt) + ")", 20, y + 11, 12, false, ink);
    line(PS("Full Days") + ": " + b.fd + "  (" + b.fd + " x " + money(b.rf) + " = " + money(b.fAmt) + ")", 20, y + 20, 12, false, ink);
    line(PS("Total Payment") + ": " + money(gross), 20, y + 29, 12, false, ink);
    line(PS("Advance") + ": - " + money(b.adv), 20, y + 38, 12, false, ink);
    line(money(gross) + " - " + money(b.adv) + " = " + money(net1), 20, y + 47, 12, false, ink);
    line(money(net1) + " + " + money(b.pend || 0) + " (" + PS("Pending payment") + ")", 20, y + 58, 12, false, ink);
    line(PS("Final Payment") + " = " + money(b.net), 20, y + 68, 16, true, teal);
    var buf = doc.output("arraybuffer");
    var fname = (b.name.replace(/[^A-Za-z0-9]+/g, "-").replace(/^-|-$/g, "") || "Duty-Log") + "-bill.pdf";
    showPdfActions(fname, buf);
    saveFile(doc, fname, buf, msg);
  }

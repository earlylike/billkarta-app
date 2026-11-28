#!/usr/bin/env python3
"""Front page: Languages pill in top-right corner, Share circle at bottom centre. Idempotent."""
import os, sys
fp = os.path.join(sys.argv[1], "frontpage", "index.html")
f = open(fp, encoding="utf-8").read()
if "BK-SWAP" in f:
    print("swapcorner: already patched"); sys.exit(0)
CSS = ("<style>/* BK-SWAP */#bkLangBtn{position:fixed;top:12px;right:12px;z-index:20;padding:7px 12px;font-size:12px;gap:6px}"
       ".bk-share{position:relative;top:auto;right:auto;left:auto;bottom:auto;transform:none;flex:none;width:37px;height:37px}.container .header p{display:none}"
       ".bk-share svg{width:15px;height:15px}</style>")
assert f.count("</head>") == 1
f = f.replace("</head>", CSS + "</head>")
open(fp, "w", encoding="utf-8").write(f)
print("swapcorner: patched")

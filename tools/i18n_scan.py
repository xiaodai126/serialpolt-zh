#!/usr/bin/env python3
# i18n_scan.py - 复查：找出仍紧跟在 UI 接口之后、且未被 tr() 包裹的裸字符串，
# 用于确认汉化覆盖度。仅报告，不修改。
import os, re

SRC = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src")
EXCLUDE = {"main.cpp", "mainwindow.cpp", "mainwindow.h",
           "defines.h", "setting_defines.h", "version.h"}

DIRECT = ("setText","setWindowTitle","setToolTip","setStatusTip","setWhatsThis",
          "setPlaceholderText","setItemText","setHeaderLabel","setLabelText",
          "setTitle","addItem","addMenu","addAction","insertMenu",
          "QAction","QMenu","QwtText","QLabel","QCheckBox","QPushButton",
          "QGroupBox","QRadioButton","setApplicationDescription")

CONTENT = r'(?:\\.|[^"])*?'

patterns = []
patterns.append(("direct", re.compile(
    r'(\b(?:' + "|".join(DIRECT) + r')\b\s*\(\s*)(")' + CONTENT + r'"', re.DOTALL)))
patterns.append(("insertTab", re.compile(
    r'(\binsertTab\s*\(\s*(?:[^"\n]*?,\s*){2})(")' + CONTENT + r'"', re.DOTALL)))
patterns.append(("QMessageBox", re.compile(
    r'QMessageBox::(warning|critical|information|question)\s*\(\s*([^,]*?),\s*(")' + CONTENT + r'"\s*,\s*(")' + CONTENT + r'"', re.DOTALL)))
patterns.append(("QCommandLineOption", re.compile(
    r'QCommandLineOption\s*\(\s*(?:\[?[^\]]*?\]\s*,|[^,]*?,\s*)(")' + CONTENT + r'"', re.DOTALL)))

def main():
    total = 0
    for root, _, files in os.walk(SRC):
        for fn in sorted(files):
            if not fn.endswith((".cpp", ".h")) or fn in EXCLUDE:
                continue
            path = os.path.join(root, fn)
            with open(path, "r", encoding="utf-8") as f:
                txt = f.read()
            for name, rx in patterns:
                for m in rx.finditer(txt):
                    lit = m.group(m.lastindex)
                    # 跳过已被 tr( 包裹的（标题/文本组）
                    seg = m.group(0)
                    if "tr(" in seg:
                        continue
                    print("[%s] %s : %s" % (name, fn, lit[:80]))
                    total += 1
    print("TOTAL remaining candidate literals: %d" % total)

if __name__ == "__main__":
    main()

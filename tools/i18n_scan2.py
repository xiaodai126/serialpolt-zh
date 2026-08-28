#!/usr/bin/env python3
# i18n_scan2.py - 广谱复查：找出所有“带空格、未被 tr() 包裹”的双引号串，
# 排除日志/设置 key/文件路径等内部串，人工过一遍补包裹。仅报告。
import os, re

SRC = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src")
EXCLUDE = {"main.cpp", "mainwindow.cpp", "mainwindow.h",
           "defines.h", "setting_defines.h", "version.h"}

literal_re = re.compile(r'"(?:\\.|[^"])*?"')
# 排除包含这些关键字的行（内部串）
SKIP_LINE = ("qDebug", "qWarning", "qCritical", "qInfo", "qFatal", "fprintf",
             "std::cerr", "<<", "SIGNAL", "SLOT", "setValue", "settings->",
             ".ini", ".svg", ".csv", ".txt", ".qrc", "QUrl", "fileName",
             "filePath", "://", "BUG_REPORT", "http", "ftp:", "setObjectName",
             "SG_", "defines.h")

def main():
    total = 0
    for root, _, files in os.walk(SRC):
        for fn in sorted(files):
            if not fn.endswith((".cpp", ".h")) or fn in EXCLUDE:
                continue
            path = os.path.join(root, fn)
            with open(path, "r", encoding="utf-8") as f:
                for lineno, line in enumerate(f, 1):
                    if line.lstrip().startswith("//"):
                        continue
                    if "tr(" in line or "translate(" in line:
                        continue
                    if any(k in line for k in SKIP_LINE):
                        continue
                    for m in literal_re.finditer(line):
                        lit = m.group(0)
                        inner = lit[1:-1]
                        # 必须含空格（像短语）且不为空、不是纯数字/枚举
                        if " " not in inner:
                            continue
                        if len(inner) < 3:
                            continue
                        print("%s:%d: %s" % (fn, lineno, lit))
                        total += 1
    print("TOTAL candidate phrase literals: %d" % total)

if __name__ == "__main__":
    main()

#!/usr/bin/env python3
# i18n_wrap.py - 为 serialplot 的用户可见英文字符串包裹 tr()，便于汉化。
#
# 设计原则（避免误包裹内部字符串）：
#   只包裹“紧跟在已知 UI 接口之后的双引号字符串字面量”，例如：
#     setText("x")  addMenu("x")  insertTab(i, w, "x")
#     QMessageBox::warning(this, "Title", "Text", ...)
#     QCommandLineOption({...}, "desc", ...)
#   以及 QAction / QMenu / QLabel 等构造函数的首个字符串参数。
#   已 tr()/translate() 的不会重复包裹。日志(qDebug 等)、设置 key、
#   文件路径、SIGNAL/SLOT 不会被匹配（它们不在上述 UI 接口后）。
#
# 用法：python3 tools/i18n_wrap.py [--dry-run]

import os
import re
import sys

SRC = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src")
EXCLUDE = {"main.cpp", "mainwindow.cpp", "mainwindow.h",
           "defines.h", "setting_defines.h", "version.h"}

# 直接包裹“紧随 ( 之后的字符串”的 UI 接口（单参数或构造参数）
DIRECT_API = (
    "setText", "setWindowTitle", "setToolTip", "setStatusTip", "setWhatsThis",
    "setPlaceholderText", "setItemText", "setHeaderLabel", "setLabelText",
    "setTitle", "addItem", "addMenu", "addAction", "insertMenu",
    "QAction", "QMenu", "QwtText", "QLabel", "QCheckBox", "QPushButton",
    "QGroupBox", "QRadioButton", "setApplicationDescription",
)

# 内容：匹配转义序列或任意非双引号字符
CONTENT = r'(?:\\.|[^"])*'

direct_re = re.compile(
    r'(\b(?:' + "|".join(DIRECT_API) + r')\b\s*\(\s*)'
    r'(")' + CONTENT + r'"'
)

insert_re = re.compile(
    r'(\binsertTab\s*\(\s*(?:[^"\n]*?,\s*){2})'
    r'(")' + CONTENT + r'"'
)

mb_re = re.compile(
    r'QMessageBox::(warning|critical|information|question)\s*\(\s*'
    r'([^,]*?),\s*'                      # parent (this / NULL)
    r'(")' + CONTENT + r'"'              # title
    r'\s*,\s*'
    r'(")' + CONTENT + r'"'              # text
)

cmdopt_re = re.compile(
    r'QCommandLineOption\s*\(\s*'
    r'(?:\[?[^\]]*?\]\s*,|[^,]*?,\s*)'  # names
    r'(")' + CONTENT + r'"'              # description
)


def wrap_direct(m):
    return m.group(1) + 'tr("' + m.group(2) + '")'


def wrap_insert(m):
    return m.group(1) + 'tr("' + m.group(2) + '")'


def wrap_mb(m):
    return (m.group(1) + "(" + m.group(2) + ', tr("' + m.group(3)
            + '"), tr("' + m.group(4) + '")')


def wrap_cmdopt(m):
    return m.group(1) + 'tr("' + m.group(2) + '")'


def process_line(line):
    stripped = line.lstrip()
    if stripped.startswith("//"):
        return line
    out = direct_re.sub(wrap_direct, line)
    out = insert_re.sub(wrap_insert, out)
    out = mb_re.sub(wrap_mb, out)
    out = cmdopt_re.sub(wrap_cmdopt, out)
    return out


def main():
    dry = "--dry-run" in sys.argv
    changed_files = 0
    changed_lines = 0
    for root, _, files in os.walk(SRC):
        for fn in files:
            if not fn.endswith((".cpp", ".h")):
                continue
            if fn in EXCLUDE:
                continue
            path = os.path.join(root, fn)
            with open(path, "r", encoding="utf-8") as f:
                lines = f.readlines()
            new_lines = [process_line(l) for l in lines]
            diff = sum(1 for a, b in zip(lines, new_lines) if a != b)
            if diff:
                changed_files += 1
                changed_lines += diff
                print("[wrap] %s: %d line(s)" % (fn, diff))
                if not dry:
                    with open(path, "w", encoding="utf-8") as f:
                        f.writelines(new_lines)
    print("Done. files=%d lines=%d" % (changed_files, changed_lines))


if __name__ == "__main__":
    main()

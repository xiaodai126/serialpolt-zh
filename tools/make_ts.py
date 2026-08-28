#!/usr/bin/env python3
# make_ts.py - 从 serialplot 源码抽取可翻译字符串，生成/填充 .ts 文件。
#
# 用法：
#   python3 tools/make_ts.py extract     # 抽取 -> translations/serialplot_zh_CN.ts(空翻译) + strings.txt
#   python3 tools/make_ts.py generate     # 用 translations/en2zh.json 回填 -> translations/serialplot_zh_CN.ts
#
# 上下文规则：
#   - .cpp/.h 中的 tr("x") : 上下文 = 所在类（由 ClassName::method 推断）
#   - .ui 中的 <string>    : 上下文 = 该 .ui 顶层 <class>
# 与 Qt uic / lupdate 的行为一致，保证运行时 tr()/translate() 能命中 .qm。

import os
import re
import sys
import json
import xml.etree.ElementTree as ET

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "src")
TRANS = os.path.join(ROOT, "translations")
TS_PATH = os.path.join(TRANS, "serialplot_zh_CN.ts")
STRINGS_TXT = os.path.join(TRANS, "strings.txt")
EN2ZH = os.path.join(TRANS, "en2zh.json")

# tr("source") 或 tr("source", "comment")
TR_RE = re.compile(
    r'(?<![\w])tr\s*\(\s*'          # tr(
    r'(")((?:\\.|[^"])*)"'          # "source"
    r'(?:\s*,\s*(")((?:\\.|[^"])*)")?'  # 可选 , "comment"
    r'\s*\)'
)

CLASS_RE = re.compile(r'^\s*class\s+(\w+)\b')
METHOD_RE = re.compile(r'\b(\w+)::(\w+)\s*\(')

# 收集项目自身类名，避免把 QString::number / QObject::connect 等 Qt 静态调用
# 误判为“当前类”而污染翻译上下文。
def collect_project_classes():
    classes = set()
    for fn in os.listdir(SRC):
        if not fn.endswith((".h", ".cpp")):
            continue
        with open(os.path.join(SRC, fn), "r", encoding="utf-8") as f:
            for line in f:
                m = CLASS_RE.match(line)
                if m:
                    classes.add(m.group(1))
    return classes


def extract_tr_from_file(path, project_classes):
    messages = []  # (context, source, comment)
    current_class = None
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            m = CLASS_RE.match(line)
            if m:
                current_class = m.group(1)
            mm = METHOD_RE.search(line)
            if mm and mm.group(1) in project_classes:
                current_class = mm.group(1)
            for tm in TR_RE.finditer(line):
                src = tm.group(2)
                comment = tm.group(4) if tm.group(4) is not None else ""
                messages.append((current_class or "", src, comment))
    return messages


def extract_from_ui(path):
    messages = []  # (context, source, comment)
    tree = ET.parse(path)
    root = tree.getroot()
    # 顶层 class 作为上下文
    cls = root.find("class")
    context = cls.text if cls is not None else os.path.basename(path)
    for string in root.iter("string"):
        if string.get("notr") in ("true", "yes"):
            continue
        text = string.text or ""
        if text == "":
            continue
        messages.append((context, text, ""))
    return messages


def collect_all():
    project_classes = collect_project_classes()
    messages = []
    for fn in sorted(os.listdir(SRC)):
        if fn.endswith(".cpp") or fn.endswith(".h"):
            messages += extract_tr_from_file(os.path.join(SRC, fn), project_classes)
    for fn in sorted(os.listdir(SRC)):
        if fn.endswith(".ui"):
            messages += extract_from_ui(os.path.join(SRC, fn))
    # 去重，保留顺序
    seen = set()
    out = []
    for ctx, src, comment in messages:
        key = (ctx, src, comment)
        if key in seen:
            continue
        seen.add(key)
        out.append((ctx, src, comment))
    return out


def esc(s):
    return (s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))


def write_skeleton(messages):
    with open(TS_PATH, "w", encoding="utf-8") as f:
        f.write('<?xml version="1.0" encoding="UTF-8"?>\n')
        f.write('<TS version="2.1" language="zh_CN">\n')
        cur_ctx = None
        for ctx, src, comment in messages:
            if ctx != cur_ctx:
                if cur_ctx is not None:
                    f.write("  </context>\n")
                f.write('  <context>\n')
                f.write("    <name>%s</name>\n" % esc(ctx))
                cur_ctx = ctx
            f.write("    <message>\n")
            f.write("      <source>%s</source>\n" % esc(src))
            if comment:
                f.write("      <comment>%s</comment>\n" % esc(comment))
            f.write("      <translation type=\"unfinished\"></translation>\n")
            f.write("    </message>\n")
        if cur_ctx is not None:
            f.write("  </context>\n")
        f.write("</TS>\n")

    with open(STRINGS_TXT, "w", encoding="utf-8") as f:
        for ctx, src, comment in messages:
            f.write("%s\t%s\n" % (ctx, src))
    print("提取完成：%d 条字符串 -> %s" % (len(messages), TS_PATH))


def generate():
    with open(EN2ZH, "r", encoding="utf-8") as f:
        en2zh = json.load(f)
    messages = collect_all()
    # key: context\x04source -> translation
    def lookup(ctx, src):
        return en2zh.get(src) or en2zh.get("%s\x04%s" % (ctx, src))
    with open(TS_PATH, "w", encoding="utf-8") as f:
        f.write('<?xml version="1.0" encoding="UTF-8"?>\n')
        f.write('<TS version="2.1" language="zh_CN">\n')
        cur_ctx = None
        done = 0
        for ctx, src, comment in messages:
            if ctx != cur_ctx:
                if cur_ctx is not None:
                    f.write("  </context>\n")
                f.write('  <context>\n')
                f.write("    <name>%s</name>\n" % esc(ctx))
                cur_ctx = ctx
            tr = lookup(ctx, src)
            f.write("    <message>\n")
            f.write("      <source>%s</source>\n" % esc(src))
            if comment:
                f.write("      <comment>%s</comment>\n" % esc(comment))
            if tr:
                f.write("      <translation>%s</translation>\n" % esc(tr))
                done += 1
            else:
                f.write("      <translation type=\"unfinished\"></translation>\n")
            f.write("    </message>\n")
        if cur_ctx is not None:
            f.write("  </context>\n")
        f.write("</TS>\n")
    print("生成 .ts 完成：%d/%d 条已翻译" % (done, len(messages)))


def main():
    if len(sys.argv) < 2 or sys.argv[1] not in ("extract", "generate"):
        print("用法: python3 tools/make_ts.py [extract|generate]")
        sys.exit(1)
    os.makedirs(TRANS, exist_ok=True)
    if sys.argv[1] == "extract":
        write_skeleton(collect_all())
    else:
        if not os.path.exists(EN2ZH):
            print("缺少 %s，无法回填翻译" % EN2ZH)
            sys.exit(1)
        generate()


if __name__ == "__main__":
    main()

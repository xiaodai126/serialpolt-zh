#!/usr/bin/env python3
# ts2qm.py - 纯 Python 实现的 .ts -> .qm 编译器（无需 lrelease / Qt 工具链）。
#
# 仅在 CMake 找不到 lrelease 时作为回退使用；正常构建由 Qt 的 lrelease 完成。
#
# 二进制格式依据 Qt6 源码：
#   - qtbase/src/corelib/kernel/qtranslator.cpp  (QTranslatorPrivate::do_load / do_translate / getMessage)
#   - qttools/src/linguist/shared/qm.cpp         (Releaser::save / writeMessage)
#
# 结构：16 字节魔数 + 若干 TLV 块（quint8 tag + quint32 大端长度 + 数据）。
#   块标签：Language=0xa7, Hashes=0x42, Messages=0x69, Contexts=0x2f, NumerusRules=0x88
#   本条实现只写 Language + Hashes + Messages 三块（省略 Contexts 块是安全的：
#   省略后 do_translate 跳过上下文快速校验，仍会在 getMessage 内按 Tag_Context 精确匹配）。
#
# 每条消息记录（字段均为大端）：
#   Translation : 0x03 + quint32(UTF-16BE 字节长, 须为偶数) + UTF-16BE 字节
#   Comment     : 0x08 + quint32(UTF-8 字节长) + UTF-8 字节   （为空则省略）
#   SourceText  : 0x06 + quint32(UTF-8 字节长) + UTF-8 字节
#   Context     : 0x07 + quint32(UTF-8 字节长) + UTF-8 字节
#   End         : 0x01
#
# Hashes 块：每条 (quint32 hash, quint32 offset) 8 字节，按 hash 升序排列。
#   hash = elfHash(source_utf8 + comment_utf8)；offset = 该消息记录在 Messages 块内的字节偏移。

import os
import sys
import struct
import xml.etree.ElementTree as ET

QM_MAGIC = bytes([
    0x3c, 0xb8, 0x64, 0x18, 0xca, 0xef, 0x9c, 0x95,
    0xcd, 0x21, 0x1c, 0xbf, 0x60, 0xa1, 0xbd, 0xdd,
])
TAG_LANGUAGE = 0xA7
TAG_HASHES = 0x42
TAG_MESSAGES = 0x69

T_TRANSLATION = 0x03
T_COMMENT = 0x08
T_SOURCETEXT = 0x06
T_CONTEXT = 0x07
T_END = 0x01


def elf_hash(ba):
    """经典 ELF 哈希（与 Qt elfHash 一致），输入字节序列，返回 uint32。"""
    h = 0
    for b in ba:
        h = (h << 4) + b
        h &= 0xFFFFFFFF
        g = h & 0xF0000000
        if g:
            h ^= (g >> 24)
        h &= ~g
        h &= 0xFFFFFFFF
    if not h:
        h = 1
    return h & 0xFFFFFFFF


def utf16be(s):
    """将 str 编码为 UTF-16BE 字节（含辅助平面代理对）。"""
    out = bytearray()
    for ch in s:
        cp = ord(ch)
        if cp <= 0xFFFF:
            out += struct.pack(">H", cp)
        else:
            cp -= 0x10000
            out += struct.pack(">H", 0xD800 + (cp >> 10))
            out += struct.pack(">H", 0xDC00 + (cp & 0x3FF))
    return bytes(out)


def parse_ts(path):
    """返回 [(context, source, comment, translation), ...]，跳过未翻译条目。"""
    tree = ET.parse(path)
    root = tree.getroot()
    msgs = []
    for ctx in root.iter("context"):
        name = ctx.find("name").text or ""
        for m in ctx.findall("message"):
            src = m.find("source").text or ""
            cm = m.find("comment")
            comment = cm.text if (cm is not None and cm.text) else ""
            tr = m.find("translation")
            translation = tr.text if (tr is not None and tr.text) else ""
            if not translation:
                continue
            msgs.append((name, src, comment, translation))
    return msgs


def build_qm(messages):
    msg_block = bytearray()
    hashes = []  # (hash, offset)

    for (context, src, comment, translation) in messages:
        rec = bytearray()
        # Translation (UTF-16BE)
        t16 = utf16be(translation)
        rec += bytes([T_TRANSLATION])
        rec += struct.pack(">I", len(t16))
        rec += t16
        # Comment (UTF-8)，为空则省略
        if comment:
            c8 = comment.encode("utf-8")
            rec += bytes([T_COMMENT])
            rec += struct.pack(">I", len(c8))
            rec += c8
        # SourceText (UTF-8)
        s8 = src.encode("utf-8")
        rec += bytes([T_SOURCETEXT])
        rec += struct.pack(">I", len(s8))
        rec += s8
        # Context (UTF-8)
        x8 = context.encode("utf-8")
        rec += bytes([T_CONTEXT])
        rec += struct.pack(">I", len(x8))
        rec += x8
        # End
        rec += bytes([T_END])

        offset = len(msg_block)
        msg_block += rec

        c8_hash = c8 if comment else b""
        h = elf_hash(s8 + c8_hash)
        hashes.append((h, offset))

    # Hashes 块按 hash 升序
    hashes.sort(key=lambda x: x[0])
    hash_block = bytearray()
    for h, off in hashes:
        hash_block += struct.pack(">II", h, off)

    # 组装文件：魔数 + Language + Hashes + Messages
    lang = b"zh_CN"
    out = bytearray()
    out += QM_MAGIC
    out += bytes([TAG_LANGUAGE])
    out += struct.pack(">I", len(lang))
    out += lang
    out += bytes([TAG_HASHES])
    out += struct.pack(">I", len(hash_block))
    out += hash_block
    out += bytes([TAG_MESSAGES])
    out += struct.pack(">I", len(msg_block))
    out += msg_block
    return bytes(out)


def main():
    if len(sys.argv) < 3:
        print("用法: python3 tools/ts2qm.py <input.ts> <output.qm>")
        sys.exit(1)
    ts_path, qm_path = sys.argv[1], sys.argv[2]
    msgs = parse_ts(ts_path)
    data = build_qm(msgs)
    with open(qm_path, "wb") as f:
        f.write(data)
    print("生成 %s : %d 条消息" % (qm_path, len(msgs)))


if __name__ == "__main__":
    main()

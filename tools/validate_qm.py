#!/usr/bin/env python3
# validate_qm.py - 用与 Qt6 qtranslator.cpp 完全一致的算法加载 .qm 并校验翻译。
# 仅用于离线自检：若本脚本能从 .qm 取到正确中文，真实 Qt 加载也应一致。
import os
import sys
import struct

QM_MAGIC = bytes([
    0x3c, 0xb8, 0x64, 0x18, 0xca, 0xef, 0x9c, 0x95,
    0xcd, 0x21, 0x1c, 0xbf, 0x60, 0xa1, 0xbd, 0xdd,
])
TAG_HASHES = 0x42
TAG_MESSAGES = 0x69

T_END = 1
T_SOURCETEXT = 6
T_CONTEXT = 7
T_COMMENT = 8
T_TRANSLATION = 3


def elf_hash(ba):
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


def read32(b, off):
    return int.from_bytes(b[off:off + 4], "big")


def read8(b, off):
    return b[off]


def match(m, ln, s, slen):
    # m: stored field bytes (UTF-8)，s: incoming UTF-8 bytes
    i = 0
    j = 0
    while ln and slen:
        if m[i] != s[j]:
            return False
        i += 1
        j += 1
        ln -= 1
        slen -= 1
    return ln == 0 and slen == 0


def get_message(m, end, context, source, comment):
    tn = None
    tn_length = 0
    context_b = context.encode("utf-8")
    source_b = source.encode("utf-8")
    comment_b = comment.encode("utf-8")
    clen = len(context_b)
    slen = len(source_b)
    cmtlen = len(comment_b)
    p = 0
    while True:
        tag = read8(m, p) if (m and p < len(m)) else 0
        p += 1
        if tag == T_END:
            break
        if tag == T_TRANSLATION:
            ln = read32(m, p)
            p += 4
            if ln & 1:
                return None
            if tn is None:
                tn_length = ln
                tn = m[p:p + ln]
            p += ln
        elif tag == T_SOURCETEXT:
            ln = read32(m, p)
            p += 4
            if not match(m[p:p + ln], ln, source_b, slen):
                return None
            p += ln
        elif tag == T_CONTEXT:
            ln = read32(m, p)
            p += 4
            if not match(m[p:p + ln], ln, context_b, clen):
                return None
            p += ln
        elif tag == T_COMMENT:
            ln = read32(m, p)
            p += 4
            if cmtlen and not match(m[p:p + ln], ln, comment_b, cmtlen):
                return None
            p += ln
        else:
            return None
    if tn is None:
        return None
    # UTF-16BE -> str
    n = tn_length // 2
    out = []
    for i in range(n):
        cp = int.from_bytes(tn[i * 2:i * 2 + 2], "big")
        out.append(cp)
    return "".join(chr(c) for c in out)


class QM:
    def __init__(self, data):
        assert data[:16] == QM_MAGIC, "bad magic"
        self.hash_array = None
        self.hash_len = 0
        self.msg_array = None
        self.msg_len = 0
        i = 16
        while i < len(data):
            tag = data[i]
            ln = read32(data, i + 1)
            body = data[i + 5:i + 5 + ln]
            if tag == TAG_HASHES:
                self.hash_array = body
                self.hash_len = ln
            elif tag == TAG_MESSAGES:
                self.msg_array = body
                self.msg_len = ln
            i += 5 + ln

    def translate(self, context, source, comment=""):
        if self.hash_array is None or self.msg_array is None:
            return None
        num_items = self.hash_len // 8
        if not num_items:
            return None
        h = elf_hash(source.encode("utf-8") + comment.encode("utf-8"))
        start = 0
        end = (num_items - 1) * 8
        # binary search
        while start <= end:
            middle = start + (((end - start) >> 4) << 3)
            rh = read32(self.hash_array, middle)
            if h == rh:
                start = middle
                break
            elif rh < h:
                start = middle + 8
            else:
                end = middle - 8
        if start > end:
            return None
        # back on equal key
        while start != 0 and read32(self.hash_array, start) == read32(self.hash_array, start - 8):
            start -= 8
        res = None
        while start < self.hash_len:
            rh = read32(self.hash_array, start)
            start += 4
            if rh != h:
                break
            ro = read32(self.hash_array, start)
            start += 4
            tn = get_message(self.msg_array[ro:], self.msg_array, context, source, comment)
            if tn is not None:
                res = tn
                break
        return res


def main():
    qm_path = sys.argv[1] if len(sys.argv) > 1 else "translations/serialplot_zh_CN.qm"
    qm = QM(open(qm_path, "rb").read())
    # (context, source, expected) 抽样校验
    cases = [
        ("MainWindow", "&File", "文件(&F)"),
        ("PlotMenu", "&View", "视图(&V)"),
        ("BPSLabel", "bits per second", "比特每秒"),
        ("FramedReader", "Sync word is invalid!", "同步字无效！"),
        ("CommandPanel", "&Commands", "命令(&C)"),
        ("CommandPanel", "Command ", "命令 "),
        ("AboutDialog", "About", "关于"),
        ("NumberFormatBox", "int8", "int8"),
        ("PortControl", "DTR", "DTR"),
        ("SnapshotView", "Ctrl+W", "Ctrl+W"),
        ("RecordPanel", "For TAB character enter \\t",
         "输入 TAB 字符请键入 \\t"),
        ("EndiannessBox", "Little Endian", "小端"),
        ("MainWindow", "SerialPlot", "SerialPlot"),
        ("MainWindow", "sps", "sps"),
    ]
    fail = 0
    for ctx, src, exp in cases:
        got = qm.translate(ctx, src)
        ok = got == exp
        if not ok:
            fail += 1
        print(("[OK] " if ok else "[FAIL] ") + "%s / %r -> %r (expect %r)" % (ctx, src, got, exp))
    # 反向校验：不存在的源应返回 None
    none_case = qm.translate("MainWindow", "ThisDoesNotExistXYZ")
    print("不存在的源返回 None:", none_case is None)
    print("FAIL 数:", fail)
    sys.exit(1 if fail else 0)


if __name__ == "__main__":
    main()

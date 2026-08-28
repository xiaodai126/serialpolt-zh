#!/usr/bin/env python3
# build_en2zh.py - 生成 translations/en2zh.json 中英对照表。
#
# 做法：从 translations/strings.txt 读取 extract 阶段得到的 (context, source) 精确列表作为键，
#       按相同顺序给出中文翻译，避免手工输入含转义引号/反斜杠的 HTML 源串导致键不匹配。
# 输出：translations/en2zh.json  (供 tools/make_ts.py generate 使用)

import os
import json

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TRANS = os.path.join(ROOT, "translations")
STRINGS_TXT = os.path.join(TRANS, "strings.txt")
EN2ZH = os.path.join(TRANS, "en2zh.json")

# 按 strings.txt 行顺序逐一给出中文翻译（共 346 条）
T = [
    # 1-5  BPSLabel
    "0bps",
    "比特每秒",
    "!%1/%2bps",
    "可能已达到最大波特率！",
    "%1bps",
    # 6-10 ChannelInfoModel
    "通道 %1",
    "通道",
    "可见",
    "增益",
    "偏移",
    # 11-13 CommandPanel
    "命令(&C)",
    "新建命令(&N)",
    "命令 ",
    # 14 DataRecorder
    "时间戳",
    # 15-17 FramedReader
    "同步字无效！",
    "帧大小必须是 %1（通道数 × 采样大小）的倍数！",
    "一切正常！",
    # 18 HidableTabWidget
    "隐藏面板",
    # 19-43 MainWindow (部分)
    "端口",
    "数据格式",
    "绘图",
    "命令",
    "记录",
    "文本视图",
    "工具栏",
    "0sps",
    "采样点/秒（每通道）",
    "正在关闭 SerialPlot",
    "存在未保存的快照。如果关闭，数据将丢失。",
    "SerialPlot 因未知错误无法保存设置：%1",
    "保存设置失败！",
    "sps",
    "导出 CSV 文件",
    "导出 SVG 文件",
    "保存设置",
    "加载设置",
    "语言",
    "语言设置将在重启后生效。",
    "用于实时绘制串口数据的小型简易软件。",
    "从文件加载配置。",
    "设置端口名称。",
    "设置端口波特率。",
    "打开串口。",
    # 44-45 Plot
    " 演示运行中 ",
    " 没有可见通道 ",
    # 46-64 PlotControlPanel
    "重置",
    "重置名称",
    "重置颜色",
    "显示全部",
    "隐藏全部",
    "重置所有增益",
    "重置所有偏移",
    "重置菜单",
    "有符号 %1 位 %2 到 +%3",
    "无符号 %1 位 %2 到 +%3",
    "-1 到 +1",
    "0 到 +1",
    "-100 到 +100",
    "0 到 +100",
    "重置通道名称与颜色",
    "显示所有通道",
    "隐藏所有通道",
    "确认采样点数",
    "不再显示此提示。",
    # 65-87 PlotMenu
    "视图(&V)",
    "网格(&G)",
    "次网格(&M)",
    "取消缩放(&U)",
    "深色背景(&D)",
    "图例(&L)",
    "多图(&P)",
    "符号(&S)",
    "缩放时显示(&Z)",
    "始终显示(&S)",
    "始终隐藏(&H)",
    "图例位置",
    "左上",
    "右上",
    "右下",
    "左下",
    "显示网格",
    "显示次网格",
    "取消绘图缩放",
    "启用深色绘图背景",
    "在绘图上显示图例",
    "分别显示所有通道",
    "显示/隐藏符号",
    # 88-93 PortControl
    "端口工具栏",
    "打开",
    "打开端口",
    "刷新端口列表",
    "未找到端口 - 请输入名称",
    "选择端口或输入名称",
    # 94-105 RecordPanel
    "记录工具栏",
    "记录",
    "仅秒",
    "带精度的秒",
    "毫秒",
    "选择记录文件",
    "错误",
    "列分隔符不能为空！请选择分隔符。",
    "文件已存在",
    "文件（%1）已存在。如何继续？",
    "覆盖",
    "选择其他文件",
    # 106-107 Snapshot
    "删除(&D)",
    "删除 ",
    # 108-115 SnapshotManager
    "快照(&S)",
    "拍摄快照(&T)",
    "加载快照(&L)",
    "清除快照(&C)",
    "拍摄当前绘图的快照",
    "从 CSV 文件加载快照",
    "删除所有快照",
    "加载 CSV 文件",
    # 116-119 SnapshotView
    "重命名快照",
    "输入新名称：",
    "导出 CSV 文件",
    "导出 SVG 文件",
    # 120 SneakyLineEdit
    "点击编辑",
    # 121-124 UpdateCheckDialog
    "更新检查失败。\\n",
    "暂无更新。",
    '发现版本 %1 的更新。点击<a href="%2">下载</a>。',
    "正在检查更新……",
    # 125-127 UpdateChecker
    "网络错误：",
    "JSON 解析错误（位于 %1）：",
    "JSON 解析错误。",
    # 128-130 AboutDialog
    "关于",
    '<html><head/><body><p align="center"><span style=" font-size:14pt;">SerialPlot</span></p>'
    '<p align="center">$VERSION_STRING$</p>'
    '<p align="center">由 Hasan Yavuz Özderya 开发</p>'
    '<p align="center">基于 Qt（<a href="https://www.qt.io/"><span style=" text-decoration: underline; color:#0000ff;">https://www.qt.io/</span></a>）'
    '与 Qwt（<a href="http://qwt.sf.net"><span style=" text-decoration: underline; color:#0000ff;">http://qwt.sf.net</span></a>）开发</p>'
    '<p align="center"><br/></p>'
    '<p align="center">本软件采用 GPL 许可证。可从 '
    '<a href="https://hg.sr.ht/~hyozd/serialplot/"><span style=" text-decoration: underline; color:#0000ff;">https://hg.sr.ht/~hyozd/serialplot/</span></a> 获取源代码。</p>'
    '<p align="center"><br/></p>'
    '<p align="right"><span style=" font-size:8pt;">版本标识： $VERSION_REVISION$<br/></span></p></body></html>',
    "关于 Qt",
    # 131-152 AsciiReaderSettings
    "表单",
    "通道数量：",
    "选择通道数量，或设为 0 表示自动（由接收数据决定）",
    "自动",
    "列分隔符：",
    "逗号",
    "空格",
    "制表符",
    "其他：",
    "输入自定义分隔符",
    "|",
    "按前缀过滤：",
    "禁用",
    "仅读取以前缀开头的行",
    "包含",
    "不读取以前缀开头的行",
    "排除",
    "用于过滤接收数据的前缀文本",
    "前缀文本",
    "数值格式：",
    "使用十六进制数据而非十进制。",
    "十六进制数据",
    # 153-161 BinaryStreamReaderSettings
    "表单",
    "通道数量：",
    "选择通道数量",
    "读取时跳过 1 字节以校正对齐",
    "跳过字节",
    "读取时跳过 1 个采样以调整通道顺序",
    "跳过采样",
    "数值类型：",
    "字节序：",
    # 162-163 CommandPanel
    "表单",
    "新建命令",
    # 164-168 CommandWidget
    "表单",
    '<html><head/><body><p>在此输入命令。</p>'
    '<p>在 ASCII 模式下，可使用反斜杠“\\”发送特殊字符。包括：<br/>'
    '<span style=" font-weight:600;">\\n</span> ：换行（Line Feed）<br/>'
    '<span style=" font-weight:600;">\\r</span> ：回车（Carriage Return）<br/>'
    '<span style=" font-weight:600;">\\t</span> ：制表符（Tab）<br/>'
    '<span style=" font-weight:600;">\\\\</span> ：反斜杠（Backslash）</p></body></html>',
    "ASCII",
    "十六进制",
    "发送",
    # 169-175 DataFormatPanel
    "数据格式",
    "数据以连续的二进制采样形式发送，可能存在同步问题。",
    "简单二进制",
    "数据以 ASCII 文本形式发送，使用逗号分隔的数值，易于实现。",
    "ASCII",
    "定义自定义二进制帧，功能强大。",
    "自定义帧",
    # 176-181 DataTextView
    "表单",
    "启用以文本形式显示绘图数据。",
    "启用",
    "行数：",
    "小数位：",
    "清除",
    # 182-185 DemoReaderSettings
    "表单",
    "通道数量：",
    "选择通道数量，或设为 0 表示自动（由接收数据决定）",
    "演示模式已启用，退出演示以修改读取设置。",
    # 186-190 EndiannessBox
    "字节序",
    "最低有效字节在前",
    "小端",
    "最高有效字节在前",
    "大端",
    # 191-213 FramedReaderSettings
    "表单",
    "以十六进制输入“帧起始”字节。",
    "通道数量",
    "# 通道：",
    "选择通道数量",
    "负载大小：",
    "帧大小固定不变",
    "固定大小：",
    '<html><head/><body><p>输入帧大小。它<span style=" font-weight:600;">必须</span>'
    '是（通道数 × 采样大小）的倍数。</p></body></html>',
    "“帧起始”字节之后的第 1 个字节应为帧负载大小，仅计算后续字节，不含校验和。",
    "1 字节长度字段",
    "“帧起始”字节之后的前 2 个字节应为帧负载大小，仅计算后续字节，不含校验和。",
    "2 字节长度字段",
    "数值类型：",
    "字节顺序",
    "字节序：",
    "校验和：",
    "帧的最后一个字节为校验和。",
    "启用",
    "帧起始：",
    "一切正常。",
    "启用额外日志输出，便于调试",
    "调试模式",
    # 214-243 MainWindow (其余)
    "SerialPlot",
    "日志",
    "错误与警告信息",
    "帮助(&H)",
    "文件(&F)",
    "次要",
    "绘图工具栏",
    "暂停",
    "暂停绘图",
    "暂停",
    "清除",
    "Ctrl+K",
    "关于(&A)",
    "演示模式(&D)",
    "切换演示模式",
    "导出 CSV(&E)",
    "将绘图数据导出为 CSV",
    "退出(&Q)",
    "Ctrl+Q",
    "报告问题(&R)",
    "在 SerialPlot 网站报告问题",
    "保存设置(&S)",
    "将设置保存到文件",
    "加载设置(&L)",
    "从文件加载设置",
    "检查更新(&C)",
    "柱状图",
    "垂直",
    "水平",
    "导出 SVG(&X)",
    # 244-260 NumberFormatBox
    "数值格式",
    "无符号 1 字节整数",
    "uint8",
    "无符号 2 字节整数",
    "uint16",
    "无符号 4 字节整数",
    "uint32",
    "有符号 1 字节整数",
    "int8",
    "有符号 2 字节整数",
    "int16",
    "有符号 4 字节整数",
    "int32",
    "4 字节浮点数",
    "float",
    "8 字节双精度浮点数",
    "double",
    # 261-275 PlotControlPanel (其余)
    "表单",
    "线宽",
    "缓冲区大小：",
    "以采样点数表示的采集长度",
    "以索引作为 X 轴",
    "X 最小值",
    "Y 轴下限",
    "X 最大值",
    "Y 轴上限",
    "Y 轴自动缩放",
    "Y 最小值",
    "Y 最大值",
    "选择范围预设：",
    "绘图宽度：",
    "X 轴宽度（绘图中显示的最大采样点数）",
    # 276-307 PortControl (其余)
    "表单",
    "端口：",
    "即使未列出，也可输入端口名称，例如伪终端。",
    "如果操作系统/适配器支持，可输入自定义波特率。",
    "波特率：",
    "刷新端口列表",
    "↺",
    "无校验",
    "奇校验",
    "偶校验",
    "8 位",
    "7 位",
    "6 位",
    "5 位",
    "1 停止位",
    "2 停止位",
    "无流控",
    "硬件流控",
    "软件流控",
    "切换端口状态",
    "请求发送",
    "数据终端就绪",
    "DTR",
    "数据设备就绪",
    "DSR",
    "RTS",
    "数据载波检测",
    "DCD",
    "振铃指示",
    "RI",
    "清除发送",
    "CTS",
    # 308-332 RecordPanel (其余)
    "表单",
    "文件名中的时间戳可使用 C 语言 `strftime` 函数的格式说明符。",
    "输入文件名或浏览",
    "选择记录文件",
    "浏览",
    "端口关闭时停止记录",
    "每次开始新记录时自动递增文件名",
    "自动递增文件名",
    "写入文件时不缓冲。若需在记录期间用其他软件打开该文件，请勾选此项。",
    "禁用缓冲",
    "使用 CR+LF 作为行尾。否则某些 Windows 软件可能无法正确显示行。记录期间不可更改。",
    "Windows 风格行尾",
    "通道名称写入记录文件首行",
    "写入表头行",
    "即使绘图暂停也继续写入记录文件",
    "暂停时记录",
    "插入时间戳（自纪元起的毫秒数）作为第一列",
    "插入时间戳",
    "列分隔符：",
    "输入 TAB 字符请键入 \\t",
    ",",
    "小数位：",
    "逗号后的小数位数",
    "时间戳格式：",
    "开始/停止记录",
    # 333-343 SnapshotView (其余)
    "主窗口",
    "快照(&S)",
    "另存为 CSV(&S)",
    "将快照保存为 CSV 文件",
    "重命名(&R)",
    "重命名此快照",
    "关闭(&C)",
    "关闭窗口",
    "Ctrl+W",
    "导出 SVG(&X)",
    "将快照导出为 SVG",
    # 344-346 UpdateCheckDialog (其余)
    "检查更新",
    "仅在每天应用首次启动时检查一次更新",
    "定期检查更新",
]


def main():
    # 读取 strings.txt 的精确 (context, source) 列表作为键，顺序与 T 对齐
    if not os.path.exists(STRINGS_TXT):
        print("缺少 %s，请先运行 make_ts.py extract" % STRINGS_TXT)
        raise SystemExit(1)
    keys = []
    with open(STRINGS_TXT, "r", encoding="utf-8") as f:
        for line in f:
            line = line.rstrip("\n")
            if not line:
                continue
            ctx, src = line.split("\t", 1)
            keys.append(src)
    if len(keys) != len(T):
        print("条目数不一致：strings.txt=%d, 翻译=%d" % (len(keys), len(T)))
        raise SystemExit(1)
    d = {}
    for src, tr in zip(keys, T):
        d[src] = tr
    with open(EN2ZH, "w", encoding="utf-8") as f:
        json.dump(d, f, ensure_ascii=False, indent=1)
    print("已生成 %s ：%d 条中英对照" % (EN2ZH, len(d)))


if __name__ == "__main__":
    main()

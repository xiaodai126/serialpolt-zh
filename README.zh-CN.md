<p align="center">
  <a href="README.md" style="padding:6px 14px;border:1px solid #d0d7de;border-radius:6px;color:#0969da;font-weight:bold;text-decoration:none;margin-right:8px;">🇬🇧 English</a>
  <span style="padding:6px 14px;border:1px solid #d0d7de;border-radius:6px;background:#0969da;color:#ffffff;font-weight:bold;">🇨🇳 简体中文</span>
</p>

# SerialPlot 中文汉化版说明

本项目在官方 [serialplot](https://github.com/hyOzd/serialplot)（v0.13.0，Qt6 串口实时波形绘图工具）基础上，
增加了完整的中文界面翻译与语言切换能力。源码树可直接 clone 编译，无需任何额外补丁。

> 关于「如何拿到汉化版」：本仓库已通过 GitHub Actions 一键构建出自带中文翻译的绿色压缩包
> `serialplot-zh_CN-portable.zip`，到仓库的 Releases 页面下载解压即用。汉化改了源码（加了翻译加载 + 语言菜单），
> 必须重新编译出带补丁的二进制；光把 `.qm` 翻译文件塞进官方原版 exe 没用——原版没有加载翻译器的代码。

## 一、功能特性

- **全量汉化**：菜单、工具栏、标签页、各类设置/读取对话框、状态栏、消息框、提示文本均已中文化。
- **三种语言切换方式**：
  1. **自动**：当系统区域为简体中文时，启动即显示中文。
  2. **手动菜单**：菜单栏「语言(Language)」下提供「中文 / English」，切换后重启生效。
  3. **命令行参数**：`serialplot --lang zh_CN` 或 `serialplot --lang=zh_CN`（英文用 `--lang en`）。
- **记忆选择**：手动选择的语言会写入 QSettings，下次启动沿用。
- **Qt 自带控件中文**：同时加载 `qtbase_zh_CN`，消息框的「确定 / 取消 / 是 / 否」等按钮也显示中文
  （需系统 Qt 自带该翻译文件）。

## 二、文件改动清单

| 文件 | 改动 |
| --- | --- |
| `src/main.cpp` | 解析 `--lang`、按「命令行 > 设置 > 系统区域」决定语言；在创建主窗口前安装 `serialplot_zh_CN` 与 `qtbase_zh_CN` 翻译器 |
| `src/mainwindow.h` / `src/mainwindow.cpp` | 新增「语言」菜单与互斥的「中文 / English」动作；`setLanguage()` 保存设置并提示重启 |
| `src/mainwindow.ui` | 新增 `menuLanguage` 菜单及 `actionLangZh` / `actionLangEn`（文本标记 `notr`，不进入翻译） |
| `src/bpslabel.cpp` | 修正并补全若干可见字符串的 `tr()` 包裹 |
| `src/updatechecker.cpp` | 补全错误消息的 `tr()` 包裹 |
| `CMakeLists.txt` | 接入翻译编译：优先 `lrelease`，回退 `tools/ts2qm.py`，最次用随源码提交的 `.qm`；构建后复制到 `translations/`，并安装到 `bin/translations` |
| `translations/serialplot_zh_CN.ts` | 翻译源文件（346 条字符串，全量已译） |
| `translations/serialplot_zh_CN.qm` | 编译后的二进制翻译（运行时加载） |
| `translations/en2zh.json` | 源文 → 译文对照表，便于批量维护 |
| `tools/make_ts.py` | 从源码 `tr()` 与 `.ui` 提取字符串，生成/回填 `.ts` |
| `tools/ts2qm.py` | 纯 Python 的 `.ts → .qm` 编译器（无需 lrelease） |
| `tools/build_en2zh.py` | 由 `strings.txt` 生成 `en2zh.json` |
| `tools/validate_qm.py` | 离线校验 `.qm` 是否能被 Qt 算法正确加载 |
| `tools/build_windows.sh` | **Windows 一键编译 + 部署 + 打包脚本（Git Bash 运行）** |
| `tools/serialplot.nsi` | **NSIS 安装包脚本（生成 `serialplot-zh_CN-setup.exe`）** |
| `.github/workflows/build-windows.yml` | **GitHub Actions 工作流（推到 GitHub 点一下自动出 exe）** |

> 说明：所有用户可见字符串均已用 `tr()` 包裹；`.ui` 文件中的文本由 `uic` 自动纳入翻译系统，无需逐处加 `tr()`。
> QSettings 内部键（如写入配置的 `Port` / `DataFormat`）**刻意不翻译**，以保证设置文件的跨语言兼容性。


## 三、语言切换说明

| 方式 | 操作 |
| --- | --- |
| 自动 | 系统区域为中文时启动即中文 |
| 手动 | 菜单「语言(Language)」→「中文」或「English」 |
| 命令行 | `serialplot --lang zh_CN`（中文） / `serialplot --lang en`（英文） |

**重要限制**：Qt 的翻译器必须在创建任何窗口之前安装，因此**切换语言后需要重启程序**才会生效
（手动切换时会弹出提示）。这与官方机制一致，非缺陷。


## 四、已知限制

- 切换语言需重启（Qt 翻译器机制限制）。
- `qtbase_zh_CN` 依赖系统 Qt 安装自带；若缺失，SerialPlot 自身文本仍为中文，但 Qt 原生控件
  （如消息框按钮）会回退为英文。
- QSettings 的配置文件键名保持英文，以保证不同语言版本之间的设置兼容。
- 目前 Qt6 SDK 的获取依赖网络；若所在网络对大型二进制包有限制，直接使用仓库 Actions 云端构建出的成品。

## 五、与原项目

本汉化以补丁形式叠加在官方 v0.13.0 之上，未改动任何业务逻辑与数据结构。如需向上游提交，
建议将 `translations/`、`tools/ts2qm.py` 及 `main.cpp` / `mainwindow.*` 的 i18n 相关改动整理为独立 PR。

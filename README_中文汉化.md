# SerialPlot 中文汉化版说明

本项目在官方 [serialplot](https://github.com/hyOzd/serialplot)（v0.13.0，Qt6 串口实时波形绘图工具）基础上，
增加了完整的中文界面翻译与语言切换能力。源码树可直接 clone 编译，无需任何额外补丁。

> 关于「为什么没有现成 exe」：汉化是改了源码（加了翻译加载 + 语言菜单），必须重新编译出带补丁的二进制；
> 光把 `.qm` 翻译文件塞进官方原版 exe 没用——原版没有加载翻译器的代码。下面提供三种拿到汉化版 exe 的方式。

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

## 三、拿到汉化版 exe 的三种方式

### 方式 A：本机编译（推荐，最可控）

**必须先装 Qt6（MinGW 版）**，因为本项目把 Qwt 静态库名写死为 `libqwt.a`，且 Qwt 的补丁命令用了 `sed`，
所以**只能用 MinGW 工具链，并且要在 Git Bash / MSYS2 里跑 cmake**（原生 cmd 没有 `sed`）。MSVC 路线会找不到库。

1. 安装 **Qt 在线安装器**（https://www.qt.io/download-qt-installer ），在「Qt 6.x」下勾选：
   - **MinGW 64-bit**（自带 Qt 运行库与 qmake）
   - 展开后确保勾选 **Qt SerialPort** 与 **Qt SVG** 两个组件（MinGW 版默认都带，留意别漏）
   - 在「Developer and Designer Tools」页勾选 **CMake** 与 **MinGW**（编译器）
2. 安装 **Git for Windows**（提供 Git Bash 与 `sed`）。
3. 编辑 `tools/build_windows.sh` 顶部的两行路径（改成你机器上的 `6.8.0/mingw_64` 与 `Tools/mingw1310_64`）。
4. 在 Git Bash 中运行：
   ```bash
   bash tools/build_windows.sh
   ```
   脚本会编译、用 `windeployqt` 收集 Qt 运行库、复制中文翻译，最后压出
   `serialplot-zh_CN-portable.zip`（解压即用，免安装）。

- `BUILD_QWT` 默认 `ON`：首次编译会**从 SourceForge 下载并编译 Qwt 6.3.0**，需要联网、耗时数分钟。
  若下载慢，可手动下载 `qwt-6.3.0.tar.bz2` 放到本地，再修改 `cmake/modules/BuildQwt.cmake` 里的 `URL` 指向本地文件。
- 若用 aqtinstall 而非官方安装器：注意个别镜像的 MinGW 模块列表可能漏掉 `qtsvg`，
  此时请用官方安装器，或自行下载 `qtsvg-everywhere-src-6.8.0.tar.xz` 用 `qmake6 && mingw32-make` 编一个放进去。

### 方式 B：做成标准安装包（基于方式 A）

方式 A 产出的是绿色 zip。若要 `.exe` 安装包：

1. 安装 [NSIS](https://nsis.sourceforge.io/Download)。
2. 先运行 `tools/build_windows.sh` 生成 `dist/` 目录。
3. 用 NSIS 编译脚本：`makensis.exe tools/serialplot.nsi`
4. 产物 `serialplot-zh_CN-setup.exe` 即标准 Windows 安装程序（含卸载）。

### 方式 C：GitHub Actions 一键出包（本机完全不用装 Qt，推荐）

把本仓库推到你自己的 GitHub 仓库，在 **Actions → "Build Windows (中文汉化版)" → Run workflow**，
工作流在云端用 Qt6 MinGW 编译并打包，对你本机零要求。构建完成后提供两种下载入口：

1. **GitHub Release（默认就有）**：每次构建自动发布到仓库的 `Releases` 页面，下载
   `serialplot-zh_CN-portable.zip` 即可（解压即用）。这是首选下载方式。
2. **Gitee 下载站（可选，国内更快）**：若希望国内下载更快，可让工作流把同一个包
   **自动同步到你的 Gitee 仓库 Release**。只需在 GitHub 仓库做一次配置：
   - 在 Gitee 生成私人令牌：Gitee → 设置 → 私人令牌 → 勾选 `projects`（仓库读写权限）→ 复制令牌（仅显示一次，妥善保存）。
   - 在 GitHub 仓库 → Settings → Secrets and variables → Actions → 新增两个 repository secret：
     - `GITEE_TOKEN`：值填上面的 Gitee 私人令牌
     - `GITEE_REPO`：值填 `你的Gitee用户名/你的Gitee仓库名`（形如 `laoda/serialplot-zh`）
   - 配置后，每次构建会自动多跑一个 `sync-to-gitee` 任务，把 zip 传到 Gitee Release；
     **未配置这两个 secret 时会自动跳过**，不影响 GitHub 侧的构建与下载。

> 说明：本汉化版的维护者曾在隔离环境尝试直接预编译，但该环境网络无法拉取 Qt 的大型二进制包，
> 故提供上述 A/B/C 三种可在你侧落地的方案。方式 C 的构建机在 GitHub 云端，网络稳定，最省心。

## 四、语言切换说明

| 方式 | 操作 |
| --- | --- |
| 自动 | 系统区域为中文时启动即中文 |
| 手动 | 菜单「语言(Language)」→「中文」或「English」 |
| 命令行 | `serialplot --lang zh_CN`（中文） / `serialplot --lang en`（英文） |

**重要限制**：Qt 的翻译器必须在创建任何窗口之前安装，因此**切换语言后需要重启程序**才会生效
（手动切换时会弹出提示）。这与官方机制一致，非缺陷。

## 五、如何修改或更新翻译

### 方法 A：直接改 `.ts`（适合少量修正）

1. 编辑 `translations/serialplot_zh_CN.ts` 中对应 `<message>` 的 `<translation>`。
2. 重新生成 `.qm`：有 `lrelease` 则 `lrelease translations/serialplot_zh_CN.ts -qm translations/serialplot_zh_CN.qm`；
   或用 `python3 tools/ts2qm.py translations/serialplot_zh_CN.ts translations/serialplot_zh_CN.qm`。

### 方法 B：批量维护 `en2zh.json`（适合整体改动）

1. 编辑 `translations/en2zh.json`（键为英文源串，值为中文译文）。
2. 重新生成 `.ts`：`python3 tools/make_ts.py generate`。
3. 再按方法 A 第 2 步生成 `.qm`。

### 提取新增字符串（需 `lupdate`）

源码或 `.ui` 新增了可见字符串时，运行：

```bash
cmake --build build --target update_translations
```

该目标会调用 `lupdate` 重新抽取并更新 `serialplot_zh_CN.ts`（已翻译内容保留，新增条目标记 `unfinished`）。

## 六、已知限制

- 切换语言需重启（Qt 翻译器机制限制）。
- `qtbase_zh_CN` 依赖系统 Qt 安装自带；若缺失，SerialPlot 自身文本仍为中文，但 Qt 原生控件
  （如消息框按钮）会回退为英文。
- QSettings 的配置文件键名保持英文，以保证不同语言版本之间的设置兼容。
- 目前 Qt6 SDK 的获取依赖网络；若所在网络对大型二进制包有限制，优先用方式 C（云端构建）。

## 七、与原项目

本汉化以补丁形式叠加在官方 v0.13.0 之上，未改动任何业务逻辑与数据结构。如需向上游提交，
建议将 `translations/`、`tools/ts2qm.py` 及 `main.cpp` / `mainwindow.*` 的 i18n 相关改动整理为独立 PR。

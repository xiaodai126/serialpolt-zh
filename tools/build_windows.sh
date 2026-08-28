#!/usr/bin/env bash
# =============================================================================
# SerialPlot 中文汉化版 —— Windows 一键构建 + 部署 + 打包脚本
#
# 在 Git Bash（或 MSYS2）中运行。本脚本会：
#   1. 用 MinGW 生成构建系统并编译（Qwt 默认自动从 SourceForge 下载编译）
#   2. 用 windeployqt 收集 Qt 运行库，做成「免安装绿色版」
#   3. 复制汉化翻译 serialplot_zh_CN.qm 与 Qt 自带中文 qtbase_zh_CN.qm
#   4. 压缩为 serialplot-zh_CN-portable.zip
#
# 用法：先把下面 QT_ROOT / MINGW_ROOT 改成你机器上的实际路径，然后：
#      bash tools/build_windows.sh
# =============================================================================
set -e

# ===================== 按你的安装修改这两行 =====================
# Qt 安装目录下的 MinGW 构建（形如 6.8.0/mingw_64）
QT_ROOT="/c/Qt/6.8.0/mingw_64"
# Qt 安装器自带的 MinGW 编译器（形如 Tools/mingw1310_64）
MINGW_ROOT="/c/Qt/Tools/mingw1310_64"
# ===============================================================

SRC="$(cd "$(dirname "$0")/.." && pwd)"
BUILD="$SRC/build"
DIST="$SRC/dist"

# 把 Qt 工具(qmake/moc/rcc/uic/windeployqt) 与 MinGW(gcc/g++/mingw32-make) 加入 PATH
export PATH="$QT_ROOT/bin:$MINGW_ROOT/bin:$PATH"

echo "==> 源码目录: $SRC"
echo "==> Qt:   $QT_ROOT"
echo "==> MinGW:$MINGW_ROOT"

echo "[1/5] 配置 cmake (MinGW Makefiles) ..."
cmake -B "$BUILD" -G "MinGW Makefiles" \
      -DCMAKE_BUILD_TYPE=Release \
      -DBUILD_QWT=ON

echo "[2/5] 编译 (首次会下载并编译 Qwt 6.3.0，需联网，可能耗时数分钟) ..."
cmake --build "$BUILD" --config Release

EXE="$BUILD/serialplot.exe"
if [ ! -f "$EXE" ]; then
  echo "错误：未找到 $EXE，编译可能失败，请检查上方输出。" >&2
  exit 1
fi

echo "[3/5] windeployqt 收集 Qt 运行库 -> $DIST"
rm -rf "$DIST"
"$QT_ROOT/bin/windeployqt.exe" "$EXE" --dir "$DIST" --release

echo "[4/5] 复制汉化翻译 ..."
mkdir -p "$DIST/translations"
cp "$SRC/translations/serialplot_zh_CN.qm" "$DIST/translations/"
if [ -f "$QT_ROOT/translations/qtbase_zh_CN.qm" ]; then
  cp "$QT_ROOT/translations/qtbase_zh_CN.qm" "$DIST/translations/"
  echo "    已复制 qtbase_zh_CN.qm（消息框按钮等原生控件中文）"
else
  echo "    警告：未找到 qtbase_zh_CN.qm，原生控件按钮将回退为英文"
fi
cp "$EXE" "$DIST/"

echo "[5/5] 压缩为绿色版 zip ..."
rm -f "$SRC/serialplot-zh_CN-portable.zip"
# 用 Windows 自带 PowerShell 压缩，避免 Git Bash 缺少 zip 命令
powershell -NoProfile -Command "Compress-Archive -Path '$(cygpath -w "$DIST")' -DestinationPath '$(cygpath -w "$SRC/serialplot-zh_CN-portable.zip")' -Force"
echo "完成：解压 $SRC/serialplot-zh_CN-portable.zip 即可运行 serialplot.exe"
echo "      如需标准安装包，用 NSIS 编译 tools/serialplot.nsi（指向 dist/ 目录）。"

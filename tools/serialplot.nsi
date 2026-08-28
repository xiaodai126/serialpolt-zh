; =============================================================================
; SerialPlot 中文汉化版 —— NSIS 安装包脚本
;
; 前提：先运行 tools/build_windows.sh 生成 dist/ 目录（含 serialplot.exe + Qt 运行库 + translations/）
; 用法：安装 NSIS 后，右键本文件 -> "Compile NSIS Script"，或在命令行：
;      makensis.exe tools/serialplot.nsi
; 产物：serialplot-zh_CN-setup.exe
; =============================================================================

!define APPNAME "SerialPlot"
!define APPVER "0.13.0"
!define PUBLISHER "SerialPlot 中文汉化版"
; dist 目录（相对于本 .nsi 文件所在的项目根/tools -> 上一级/dist）
!define DISTDIR "..\dist"

Name "${APPNAME} ${APPVER} (中文汉化版)"
OutFile "serialplot-zh_CN-setup.exe"
InstallDir "$PROGRAMFILES64\${APPNAME}"
InstallDirRegKey HKLM "Software\${APPNAME}" "InstallDir"

RequestExecutionLevel admin
Unicode true

Page directory
Page instfiles
UninstPage uninstConfirm

Section "主程序 (必选)" SEC_MAIN
  SetOutPath "$INSTDIR"
  ; 递归复制 dist/ 下全部文件（exe + Qt DLL + translations/）
  File /r "${DISTDIR}\*.*"

  ; 开始菜单快捷方式
  CreateDirectory "$SMPROGRAMS\${APPNAME}"
  CreateShortCut "$SMPROGRAMS\${APPNAME}\${APPNAME}.lnk" "$INSTDIR\serialplot.exe"
  CreateShortCut "$SMPROGRAMS\${APPNAME}\卸载.lnk" "$INSTDIR\uninstall.exe"

  ; 桌面快捷方式
  CreateShortCut "$DESKTOP\${APPNAME} (中文).lnk" "$INSTDIR\serialplot.exe"

  ; 卸载信息
  WriteUninstaller "$INSTDIR\uninstall.exe"
  WriteRegStr HKLM "Software\${APPNAME}" "InstallDir" "$INSTDIR"
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" \
    "DisplayName" "${APPNAME} ${APPVER} (中文汉化版)"
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" \
    "UninstallString" "$INSTDIR\uninstall.exe"
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" \
    "Publisher" "${PUBLISHER}"
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" \
    "DisplayVersion" "${APPVER}"
SectionEnd

Section "Uninstall"
  RMDir /r "$INSTDIR"
  Delete "$SMPROGRAMS\${APPNAME}\${APPNAME}.lnk"
  Delete "$SMPROGRAMS\${APPNAME}\卸载.lnk"
  RMDir "$SMPROGRAMS\${APPNAME}"
  Delete "$DESKTOP\${APPNAME} (中文).lnk"
  DeleteRegKey HKLM "Software\${APPNAME}"
  DeleteRegKey HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}"
SectionEnd

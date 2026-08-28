/*
  Copyright © 2020 Hasan Yavuz Özderya

  This file is part of serialplot.

  serialplot is free software: you can redistribute it and/or modify
  it under the terms of the GNU General Public License as published by
  the Free Software Foundation, either version 3 of the License, or
  (at your option) any later version.

  serialplot is distributed in the hope that it will be useful,
  but WITHOUT ANY WARRANTY; without even the implied warranty of
  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
  GNU General Public License for more details.

  You should have received a copy of the GNU General Public License
  along with serialplot.  If not, see <http://www.gnu.org/licenses/>.
*/

#include <QApplication>
#include <QtGlobal>
#include <QIcon>
#include <QTranslator>
#include <QLocale>
#include <QSettings>
#include <iostream>

#include "mainwindow.h"
#include "tooltipfilter.h"
#include "version.h"

MainWindow* pMainWindow = nullptr;

// 解析命令行 --lang 参数，支持 "--lang zh_CN" 与 "--lang=zh_CN" 两种写法
static QString getLangArg(int argc, char* argv[])
{
    for (int i = 1; i < argc; ++i)
    {
        QString arg = QString::fromLocal8Bit(argv[i]);
        if (arg == "--lang" && i + 1 < argc)
            return QString::fromLocal8Bit(argv[i + 1]).toLower();
        if (arg.startsWith("--lang="))
            return arg.mid(7).toLower();
    }
    return QString();
}

// 决定界面语言：命令行 > 已保存设置 > 系统区域
static QString determineLanguage(int argc, char* argv[])
{
    QString lang = getLangArg(argc, argv);
    if (!lang.isEmpty())
        return lang;

    QSettings settings(PROGRAM_NAME, PROGRAM_NAME);
    lang = settings.value("Language").toString().toLower();
    if (!lang.isEmpty())
        return lang;

    if (QLocale::system().language() == QLocale::Chinese)
        return "zh_cn";

    return "en";
}

void messageHandler(QtMsgType type, const QMessageLogContext &context,
                    const QString &msg)
{
    QString logString;

    switch (type)
    {
#if (QT_VERSION >= QT_VERSION_CHECK(5, 5, 0))
        case QtInfoMsg:
            logString = "[Info] " + msg;
            break;
#endif
        case QtDebugMsg:
            logString = "[Debug] " + msg;
            break;
        case QtWarningMsg:
            logString = "[Warning] " + msg;
            break;
        case QtCriticalMsg:
            logString = "[Error] " + msg;
            break;
        case QtFatalMsg:
            logString = "[Fatal] " + msg;
            break;
    }

    std::cerr << logString.toStdString() << std::endl;

    if (pMainWindow != nullptr)
    {
        // TODO: don't call MainWindow::messageHandler if window is destroyed
        pMainWindow->messageHandler(type, logString, msg);
    }

    if (type == QtFatalMsg)
    {
        __builtin_trap();
    }
}

int main(int argc, char *argv[])
{
    QApplication a(argc, argv);
    QApplication::setApplicationName(PROGRAM_NAME);
    QApplication::setApplicationVersion(VERSION_STRING);

    // 安装界面翻译器（中文）
    QString lang = determineLanguage(argc, argv);
    if (lang.startsWith("zh"))
    {
        QStringList transPaths = {
            QCoreApplication::applicationDirPath() + "/translations",
            QCoreApplication::applicationDirPath(),
            ":/translations"
        };

        QTranslator* translator = new QTranslator(&a);
        for (const QString& p : transPaths)
        {
            if (translator->load("serialplot_zh_CN", p))
                break;
        }
        a.installTranslator(translator);

        // 同时加载 Qt 自带控件的中文翻译（如消息框的“确定/取消”按钮）
        QTranslator* qtTranslator = new QTranslator(&a);
        for (const QString& p : transPaths)
        {
            if (qtTranslator->load("qtbase_zh_CN", p))
            {
                a.installTranslator(qtTranslator);
                break;
            }
        }
    }

#ifdef Q_OS_WIN
    QIcon::setFallbackSearchPaths(QIcon::fallbackSearchPaths() << ":icons");
    QIcon::setThemeName("tango");
#endif

    qInstallMessageHandler(messageHandler);
    MainWindow w;
    pMainWindow = &w;

    ToolTipFilter ttf;
    a.installEventFilter(&ttf);

    // log application information
    qDebug() << "SerialPlot" << VERSION_STRING;
    qDebug() << "Revision" << VERSION_REVISION;

    w.show();

    return a.exec();
}

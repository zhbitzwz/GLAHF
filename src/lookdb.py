# -*- coding: utf-8 -*-
from PyQt4 import QtGui,QtCore
from PyQt4.Qt import *
from PyQt4.QtCore import QTextCodec
import os
import sys
import util
try:
    import cPickle as pickle
except ImportError:
    import pickle

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)

QTextCodec.setCodecForTr(QTextCodec.codecForName("utf8"))

class Ui_Table(QtGui.QTableWidget):
    def __init__(self,parent=None):
        super(Ui_Table,self).__init__(parent)

        self.shadow = QtGui.QGraphicsDropShadowEffect(self)
        self.shadow.setBlurRadius(5)
        self.shadow.setOffset(15,15)
        self.setGraphicsEffect(self.shadow)

        self.setWindowFlags(Qt.WindowStaysOnTopHint)


        self.setWindowTitle(self.tr("数据库"))
        self.resize(700,350)

        count = len(util.db_array())

        self.setColumnCount(4)
        self.setRowCount(count)

        strList=QtCore.QStringList()
        strList.append(self.tr("日期"))
        strList.append(self.tr("路径"))
        strList.append(self.tr("查看"))
        strList.append(self.tr("删除"))
        self.setHorizontalHeaderLabels(strList)

        with open('db.pkl','rb') as pkl:
            try:
                import os
                arr = pickle.load(pkl)
                for idx,d in enumerate(arr):
                    if os.path.exists(d.get('path')):
                        self.setRowData(idx,d.get('date'),d.get('path'),str(d.get('units')))
                    else:
                        self.setRowData(idx,d.get('date'),"文件已被删除")
            except:
                pass

    def setRowData(self, row, date, path, units):
        dateLabel = QtGui.QLabel()
        dateLabel.setText(date)
        self.setCellWidget(row, 0, dateLabel)
        self.setColumnWidth(0, 130)

        pathLabel = QtGui.QLabel()
        pathLabel.setText(_translate("Ui_Table",path,None))
        self.setCellWidget(row, 1, pathLabel)
        self.setColumnWidth(1, 350)

        analyseButton = QtGui.QPushButton()
        analyseButton.setText(_translate("Ui_Table","查看分析",None))
        analyseButton.setStyleSheet("QPushButton{border:1px solid lightgray;background:rgb(230,230,230)}"
            "QPushButton:hover{border-color:green;background:transparent}")
        self.setCellWidget(row, 2, analyseButton)

        deleteButton = QtGui.QPushButton()
        deleteButton.setText(_translate("Ui_Table","删除",None))
        deleteButton.setStyleSheet("QPushButton{border:1px solid lightgray;background:rgb(230,230,230)}"
            "QPushButton:hover{border-color:green;background:transparent}")
        self.setCellWidget(row, 3, deleteButton)

        deleteButton.clicked.connect(lambda: self.remove_button(row))
        analyseButton.clicked.connect(lambda: self.on_button(path,units))

    def on_button(self, path, units):
        import analyse
        self.analyseWindow = analyse.Ui_MainWindow(None, eval(units))
        self.analyseWindow.show()
        self.close()
        self.analyseWindow.setPreview(path)

    def remove_button(self, row):
        arr = util.db_array()
        with open('db.pkl','rb') as pkl:
            try:
                d = arr.pop(int(row))
                path = d.get('path')
                if os.path.exists(path):
                    try:
                        os.remove(d.get('path'))
                        os.remove(d.get('path')[:-4]+'_preview.jpg')
                    except:
                        pass
                self.clearContents()
            except:
                pass
        util.direct_write_db(arr)
        arr = util.db_array()
        try:
            for idx,d in enumerate(arr):
                if os.path.exists(d.get('path')):
                    self.setRowData(idx,d.get('date'),d.get('path'),str(d.get('units')))
                else:
                    self.setRowData(idx,d.get('date'),"文件已被删除")
        except:
            pass

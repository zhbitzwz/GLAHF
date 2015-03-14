# -*- coding: utf-8 -*-

from PyQt4 import QtCore, QtGui
from common import *
import cv2
import util
import json
import lookdb
import analyse
import configdialog
import faceutil
import enlarge
import time

SAVEPATH = './'
with open('settings.json') as jsonfile:
    SAVEPATH = json.load(jsonfile)['savedir']


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

FRONTALPATH = None
FRONTALIMG = None
FSCALE = None

class Ui_MainWindow(QtGui.QWidget):

    def setupUi(self, MainWindow):
        MainWindow.setObjectName(_fromUtf8("MainWindow"))
        MainWindow.resize(1350, 700)
        self.linesArr = None

        self.success_png = QtGui.QPixmap("./sys/img/success.png")
        self.fail_png = QtGui.QPixmap("./sys/img/fail.png")

        png=QtGui.QPixmap(self)
        png.load("./sys/img/mbg.png")
        palette1 = QtGui.QPalette(self)
        palette1.setBrush(self.backgroundRole(), QtGui.QBrush(png))
        MainWindow.setPalette(palette1);
        MainWindow.setAutoFillBackground(True)

        self.centralwidget = QtGui.QWidget(MainWindow)
        self.centralwidget.setObjectName(_fromUtf8("centralwidget"))
        self.analyseButton = QtGui.QPushButton(self.centralwidget)
        self.analyseButton.setEnabled(True)
        self.analyseButton.setGeometry(QtCore.QRect(70, 460, 210, 120))
        self.analyseButton.setObjectName(_fromUtf8("analyseButton"))
        self.dbButton = QtGui.QPushButton(self.centralwidget)
        self.dbButton.setEnabled(True)
        self.dbButton.setGeometry(QtCore.QRect(380, 460, 210, 120))
        self.dbButton.setObjectName(_fromUtf8("dbButton"))
        self.settingButton = QtGui.QPushButton(self.centralwidget)
        self.settingButton.setEnabled(True)
        self.settingButton.setGeometry(QtCore.QRect(710, 460, 210, 120))
        self.settingButton.setObjectName(_fromUtf8("settingButton"))
        self.exitButton = QtGui.QPushButton(self.centralwidget)
        self.exitButton.setEnabled(True)
        self.exitButton.setGeometry(QtCore.QRect(1020, 460, 210, 120))
        self.exitButton.setObjectName(_fromUtf8("exitButton"))
        self.frontalLabel = QtGui.QLabel(self.centralwidget)
        self.frontalLabel.setGeometry(QtCore.QRect(150, 30, 450, 370))
        self.frontalLabel.setObjectName(_fromUtf8("frontalLabel"))
        self.frontalLabel.setScaledContents(True)

        self.dectected_png =QtGui.QLabel(self.centralwidget)
        self.dectected_png.setGeometry(QtCore.QRect(790, 280, 120, 120))
        self.dectected_label =QtGui.QLabel(self.centralwidget)
        self.dectected_label.setGeometry(QtCore.QRect(830, 400, 80, 40))

        self.chooseFrontalFace = QtGui.QPushButton(self.centralwidget)
        self.chooseFrontalFace.setGeometry(QtCore.QRect(790, 60, 280, 100))
        self.chooseFrontalFace.setObjectName(_fromUtf8("chooseFrontalFace"))
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtGui.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 1350, 23))
        self.menubar.setObjectName(_fromUtf8("menubar"))
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtGui.QStatusBar(MainWindow)
        self.statusbar.setObjectName(_fromUtf8("statusbar"))
        MainWindow.setStatusBar(self.statusbar)

        self.frontalScale = QtGui.QSlider(MainWindow)
        self.frontalScale.setGeometry(QtCore.QRect(860, 190, 160, 40))
        self.frontalScale.setOrientation(QtCore.Qt.Horizontal)
        self.frontalScale.setObjectName(_fromUtf8("leftScale"))
        self.frontalScale.setRange(0, 3)
        self.frontalScaleLabel = QtGui.QLabel(MainWindow)
        self.frontalScaleLabel.setGeometry(QtCore.QRect(790, 200, 60, 16))
        self.frontalScaleLabel.setObjectName(_fromUtf8("rightScaleLabel"))

        self.frontallcdNum = QtGui.QLCDNumber(MainWindow)
        self.frontallcdNum.setGeometry(QtCore.QRect(1050, 200, 64, 23))
        self.frontallcdNum.setObjectName(_fromUtf8("rightlcdNum"))
        self.frontallcdNum.display(1.0)

        self.settingsdialog = configdialog.Ui_Dialog()
        self.dbdialog = lookdb.Ui_Table()
        self.connect(self.frontalScale, QtCore.SIGNAL("valueChanged(int)"),self.frontalSliderChange)
        self.connect(self.analyseButton,QtCore.SIGNAL('clicked()'),self.beginAnalyse)
        self.connect(self.dbButton,QtCore.SIGNAL('clicked()'),self.dbdialog.show)
        self.connect(self.settingButton,QtCore.SIGNAL('clicked()'),self.settingsdialog.show)
        self.connect(self.exitButton,QtCore.SIGNAL('clicked()'),QtGui.qApp,QtCore.SLOT('quit()'))
        self.connect(self.chooseFrontalFace,QtCore.SIGNAL('clicked()'),self.getfrontal)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(_translate("MainWindow", "人脸灰度值定位", None))
        self.analyseButton.setText(_translate("MainWindow", "灰度值分析", None))
        self.dbButton.setText(_translate("MainWindow", "数据库", None))
        self.settingButton.setText(_translate("MainWindow", "设置", None))
        self.exitButton.setText(_translate("MainWindow", "退出", None))
        self.frontalLabel.setText(_translate("MainWindow", "正脸", None))
        self.chooseFrontalFace.setText(_translate("MainWindow", "选择正脸", None))
        self.frontalScaleLabel.setText(_translate("Dialog", "缩放比例", None))

        BtnStyle = "QPushButton{border-radius:5px;background:rgb(110, 190, 10);color:white}"\
            "QPushButton:hover{background:rgb(140, 220, 35)}"
        pixmap = QtGui.QPixmap("./sys/img/power.png")

        self.chooseFrontalFace.setIcon(QtGui.QIcon(pixmap))
        self.chooseFrontalFace.setIconSize(pixmap.size())
        self.chooseFrontalFace.setFixedSize(280, 100)
        self.chooseFrontalFace.setStyleSheet(BtnStyle)

        BtnStyle = "QPushButton{border:1px solid lightgray;background:rgb(230,230,230)}"\
            "QPushButton:hover{border-color:green;background:transparent}"
        self.analyseButton.setStyleSheet(BtnStyle)
        self.dbButton.setStyleSheet(BtnStyle)
        self.settingButton.setStyleSheet(BtnStyle)
        self.exitButton.setStyleSheet(BtnStyle)
        for idx in [self.analyseButton,self.dbButton,
                            self.settingButton,self.exitButton]:
            shadow = QtGui.QGraphicsDropShadowEffect(self)
            shadow.setBlurRadius(15)
            shadow.setOffset(2,2)
            idx.setGraphicsEffect(shadow)

        self.frontalLabel.setPixmap(QtGui.QPixmap(INIT_FRONTALIMG))

    def frontalSliderChange(self):
        global FSCALE
        t0 = time.time()
        FRONTALTEMP = None
        value = self.frontalScale.value()
        value = float(value)/10
        FSCALE = value/2
        self.frontallcdNum.display(value+1)
        FRONTALTEMP = enlarge.enlargeimage(FACEAJUSTPATH,FSCALE,True)
        self.linesArr,status = faceutil.markdetect(FRONTALTEMP)
        self.display_dectected_result(status)
        cv2.imwrite(FRONTALTEMPPATH,FRONTALTEMP)
        self.frontalLabel.setPixmap(QtGui.QPixmap(FRONTALTEMPPATH))
        t4 = time.time()
        print t1 - t0
        print t2 - t1
        print t3 - t2
        print t4 - t1

    def getfrontal(self):
        global FRONTALPATH
        global FRONTALIMG
        FRONTALPATH = unicode(self.showFileDialog())
        if FRONTALPATH != "":
            FRONTALPATH = FRONTALPATH.encode('gbk')
            IMG = faceutil.adjustface(FRONTALPATH)
            self.linesArr,counts = faceutil.markdetect(IMG)
            self.display_dectected_result(counts)
            cv2.imwrite(FACEAJUSTPATH,IMG)
            FRONTALIMG = QtGui.QPixmap(r''+FACEAJUSTPATH)
            global FSCALE
            if FSCALE is not None and FSCALE >0:
                self.frontalSliderChange()
            else:
                self.frontalLabel.setPixmap(FRONTALIMG)

    def display_dectected_result(self, status):
        if status is True:
            self.display_status(True, "识别成功")
        else:
            self.display_status(False, "识别失败")

    def display_status(self, status, word):
        if status is True:
            self.dectected_png.setPixmap(self.success_png)
        else:
            self.dectected_png.setPixmap(self.fail_png)
        self.dectected_label.setText(_translate("MainWindow",word,None))


    def showFileDialog(self):
        filename = QtGui.QFileDialog.getOpenFileName(self,u'打开图片','./')
        return filename

    def beginAnalyse(self):
        global FRONTALIMG
        if FRONTALIMG is None:
            self.display_status(False, "请选择图片")
        d = faceutil.dealImages(FRONTALPATH,SAVEPATH,
                                    dict(FSCALE=FSCALE))

        if d is False:
            return
        else:
            util.insert_to_db(d)
            id = int(d.get('id'))-1
            self.dbdialog.insertRow(id)
            self.dbdialog.setRowData(id, d.get('date'), d.get('path'), str(d.get('units')))
        self.analysewindow = analyse.Ui_MainWindow(None,None,self.linesArr)
        self.analysewindow.show()
        self.analysewindow.setPreview(d.get('path'))

